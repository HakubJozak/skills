#!/usr/bin/env ruby
# frozen_string_literal: true

# Fetch Ruby gem documentation in AI-friendly markdown format
# Usage: fetch-gem-docs.rb <gemname> [output_dir]
#
# Sources (in priority order):
# 1. GitHub Wiki (comprehensive docs for many gems)
# 2. agent-context files (if gem supports it)
# 3. GitHub README
# 4. Local gem docs (README, examples, etc.)
# 5. YARD-generated API docs

require "bundler/setup" rescue nil
require "json"
require "fileutils"
require "open3"
require "net/http"
require "uri"
require "openssl"

class GemDocsFetcher
  GITHUB_API = "https://api.github.com"
  GITHUB_RAW = "https://raw.githubusercontent.com"

  def initialize(gem_name, output_dir = nil)
    @gem_name = gem_name
    @output_dir = output_dir || File.join(Dir.pwd, "doc", "gems")
    @output_file = File.join(@output_dir, "#{gem_name}.md")
    @sections = []
    @github_owner = nil
    @github_repo = nil
  end

  def call
    puts "Fetching documentation for: #{@gem_name}"

    spec = find_gem_spec
    unless spec
      warn "Gem '#{@gem_name}' not found. Is it in your Gemfile?"
      exit 1
    end

    puts "  Version: #{spec.version}"
    puts "  Homepage: #{spec.homepage}"

    extract_github_info(spec)
    FileUtils.mkdir_p(@output_dir)

    add_header(spec)
    fetch_github_wiki
    fetch_agent_context(spec)
    fetch_github_readme
    fetch_local_docs(spec)
    fetch_yard_docs(spec)

    write_output
    puts "\nDocumentation saved to: #{@output_file}"
  end

  private

  def find_gem_spec
    Gem::Specification.find_by_name(@gem_name)
  rescue Gem::MissingSpecError
    begin
      Bundler.definition.specs.find { |s| s.name == @gem_name }
    rescue StandardError
      nil
    end
  end

  def extract_github_info(spec)
    urls = [
      spec.homepage,
      spec.metadata["source_code_uri"],
      spec.metadata["homepage_uri"],
      spec.metadata["changelog_uri"]
    ].compact

    urls.each do |url|
      if (match = url.to_s.match(%r{github\.com[/:]([^/]+)/([^/.\s]+)}))
        @github_owner = match[1]
        @github_repo = match[2].sub(/\.git$/, "")
        puts "  GitHub: #{@github_owner}/#{@github_repo}"
        return
      end
    end
  end

  def add_header(spec)
    @sections << <<~MD
      # #{spec.name} Documentation

      > **Version:** #{spec.version} | **License:** #{spec.license || "Unknown"}
      > **Homepage:** #{spec.homepage || "N/A"}

      #{spec.summary}

      #{spec.description if spec.description != spec.summary}
    MD
  end

  def fetch_github_wiki
    return unless @github_owner && @github_repo

    puts "  Checking for GitHub Wiki..."

    # First check if wiki exists by fetching the wiki home page
    wiki_home_url = "https://raw.githubusercontent.com/wiki/#{@github_owner}/#{@github_repo}/Home.md"
    home_content = fetch_url(wiki_home_url)

    # Check for actual 404 page (not just "404" mentioned in text)
    unless home_content && home_content.length > 100 && !home_content.start_with?("404:")
      puts "    No wiki found"
      return
    end

    puts "    Wiki found! Fetching pages..."

    # Fetch wiki page list from GitHub API
    wiki_pages = discover_wiki_pages

    if wiki_pages.empty?
      puts "    Could not discover wiki pages, using common patterns"
      wiki_pages = common_wiki_pages
    end

    content = ["## Documentation\n"]
    fetched_count = 0

    wiki_pages.each do |page|
      page_url = "https://raw.githubusercontent.com/wiki/#{@github_owner}/#{@github_repo}/#{page}.md"
      page_content = fetch_url(page_url)

      next unless page_content && page_content.strip.length > 50 && !page_content.start_with?("404:")

      fetched_count += 1
      title = page.tr("-", " ").gsub(/%[0-9A-F]{2}/) { |m| [m[1..2].to_i(16)].pack("C") }

      # Skip Home if it's just a table of contents
      if page == "Home" && page_content.lines.count { |l| l.start_with?("*", "-", "1.") } > page_content.lines.count / 2
        next
      end

      content << "### #{title}\n"
      content << clean_wiki_content(page_content)
      content << "\n\n"

      print "."
    end

    puts " (#{fetched_count} pages)"

    @sections << content.join("\n") if fetched_count > 0
  end

  def discover_wiki_pages
    # Try to get wiki pages from the Home page links
    wiki_home_url = "https://raw.githubusercontent.com/wiki/#{@github_owner}/#{@github_repo}/Home.md"
    home_content = fetch_url(wiki_home_url)
    return [] unless home_content

    pages = []

    # Extract GitHub wiki-style links: [[Page Name]] or [[Page Name|Display Text]]
    home_content.scan(/\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/).each do |match|
      page_name = match[0].strip
      # Convert "Page Name" to "Page-Name" for URL
      pages << page_name.tr(" ", "-")
    end

    # Also extract standard markdown links to relative pages
    home_content.scan(/\[([^\]]+)\]\(([^)]+)\)/).each do |_text, url|
      next if url.include?("://") # Skip external URLs
      page = url.sub(%r{^\./}, "").sub(/\.md$/, "").sub(%r{^/}, "")
      pages << page unless page.empty?
    end

    # Add Home itself
    pages.unshift("Home") unless pages.include?("Home")

    pages.uniq
  end

  def common_wiki_pages
    # Common wiki page names for Ruby gems
    %w[
      Home
      Getting-Started
      Installation
      Configuration
      Usage
      Basic-Usage
      Making-Requests
      Passing-Parameters
      Response-Handling
      Headers
      Authorization-Header
      Authentication
      Cookies
      HTTPS
      SSL
      TLS
      Redirects
      Persistent-Connections
      Persistent-Connections-%28keep-alive%29
      Timeouts
      Proxy-Support
      Thread-Safety
      Compression
      Logging
      Logging-and-Instrumentation
      Instrumentation
      Errors
      Errors-and-Exceptions
      Exceptions
      Testing
      Examples
      API
      Advanced
      Advanced-Usage
      Middleware
      Plugins
      Extensions
      FAQ
      Troubleshooting
      Migration
      Upgrading
      Changelog
      Disabling-URI-Normalization
    ]
  end

  def clean_wiki_content(content)
    content
      .gsub(/\[\[([^\]|]+)\|([^\]]+)\]\]/, '[\2](#\1)') # [[Page|Text]] -> [Text](#Page)
      .gsub(/\[\[([^\]]+)\]\]/, '[\1](#\1)')            # [[Page]] -> [Page](#Page)
      .gsub(/^#+\s*$/, "")                              # Remove empty headers
      .strip
  end

  def fetch_agent_context(spec)
    context_dir = File.join(spec.gem_dir, "context")
    return unless File.directory?(context_dir)

    puts "  Found agent-context files"
    content = ["## Agent Context\n"]

    Dir.glob(File.join(context_dir, "*.md")).sort.each do |file|
      content << "### #{File.basename(file, ".md").tr("-", " ").capitalize}\n"
      content << File.read(file)
      content << "\n"
    end

    @sections << content.join("\n") if content.length > 1
  end

  def fetch_github_readme
    return unless @github_owner && @github_repo

    # Skip if we already have wiki docs (README is usually less comprehensive)
    return if @sections.any? { |s| s.include?("## Documentation") }

    puts "  Fetching GitHub README..."

    %w[README.md README.rdoc README.txt README].each do |filename|
      url = "#{GITHUB_RAW}/#{@github_owner}/#{@github_repo}/HEAD/#{filename}"
      content = fetch_url(url)

      if content && !content.empty? && !content.include?("404")
        content = convert_rdoc(content) if filename.end_with?(".rdoc")
        @sections << "## README\n\n#{content}"
        return
      end
    end
  rescue StandardError => e
    puts "    Warning: Could not fetch README: #{e.message}"
  end

  def fetch_local_docs(spec)
    gem_dir = spec.gem_dir

    # Look for examples
    examples_dir = File.join(gem_dir, "examples")
    if File.directory?(examples_dir)
      examples = Dir.glob(File.join(examples_dir, "*.rb")).first(5)
      if examples.any?
        content = ["## Examples\n"]
        examples.each do |ex|
          content << "### #{File.basename(ex)}\n"
          content << "```ruby\n#{File.read(ex)}\n```\n"
        end
        @sections << content.join("\n")
      end
    end

    # Look for additional docs folder
    %w[doc docs].each do |docs_folder|
      docs_dir = File.join(gem_dir, docs_folder)
      next unless File.directory?(docs_dir)

      md_files = Dir.glob(File.join(docs_dir, "**", "*.md")).first(10)
      next if md_files.empty?

      content = ["## Additional Documentation\n"]
      md_files.each do |file|
        relative_path = file.sub("#{docs_dir}/", "")
        doc_content = File.read(file)
        next if doc_content.strip.empty?

        content << "### #{relative_path}\n"
        content << doc_content
        content << "\n"
      end
      @sections << content.join("\n") if content.length > 1
    end

    # Look for changelog (abbreviated)
    %w[CHANGELOG.md CHANGELOG HISTORY.md CHANGES.md].each do |file|
      path = File.join(gem_dir, file)
      next unless File.exist?(path)

      content = File.read(path)
      lines = content.lines.first(80)
      @sections << "## Changelog (Recent)\n\n#{lines.join}"
      break
    end
  end

  def fetch_yard_docs(spec)
    gem_dir = spec.gem_dir
    lib_dir = File.join(gem_dir, "lib")
    return unless File.directory?(lib_dir)

    # Check if yard is available
    yard_available = system("which yardoc > /dev/null 2>&1")
    return unless yard_available

    puts "  Generating YARD API documentation..."

    temp_dir = File.join(Dir.tmpdir, "yard-#{@gem_name}-#{$$}")
    FileUtils.mkdir_p(temp_dir)

    begin
      # Generate with yard-markdown if available, otherwise standard yard
      cmd = "cd #{gem_dir} && yardoc --format=markdown -o #{temp_dir} -q 2>/dev/null"
      system(cmd)

      md_files = Dir.glob(File.join(temp_dir, "**", "*.md"))

      if md_files.any?
        content = ["## API Reference\n"]

        md_files.sort.first(15).each do |file|
          doc = File.read(file)
          next if doc.strip.empty?

          content << doc
          content << "\n---\n"
        end

        @sections << content.join("\n") if content.length > 1
      end
    ensure
      FileUtils.rm_rf(temp_dir)
    end
  end

  def fetch_url(url, max_redirects = 3)
    return nil if max_redirects <= 0

    # Try using curl first (more reliable with SSL)
    output, status = Open3.capture2("curl", "-sL", "--max-time", "15", url)
    return output if status.success? && !output.empty? && output.length > 10

    # Fallback to Net::HTTP
    uri = URI.parse(url)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = (uri.scheme == "https")
    http.verify_mode = OpenSSL::SSL::VERIFY_PEER
    http.open_timeout = 10
    http.read_timeout = 15

    request = Net::HTTP::Get.new(uri.request_uri)
    request["User-Agent"] = "GemDocsFetcher/1.0 (Ruby)"
    request["Accept"] = "text/plain, text/markdown, */*"

    response = http.request(request)

    case response
    when Net::HTTPSuccess
      response.body
    when Net::HTTPRedirection
      fetch_url(response["location"], max_redirects - 1)
    else
      nil
    end
  rescue StandardError
    nil
  end

  def convert_rdoc(content)
    content
      .gsub(/^=====\s*(.+)$/, '##### \1')
      .gsub(/^====\s*(.+)$/, '#### \1')
      .gsub(/^===\s*(.+)$/, '### \1')
      .gsub(/^==\s*(.+)$/, '## \1')
      .gsub(/^=\s*(.+)$/, '# \1')
      .gsub(/\+(\w+)\+/, '`\1`')
      .gsub(/\*(\w+)\*/, '**\1**')
      .gsub(/_(\w+)_/, '*\1*')
  end

  def write_output
    if @sections.length <= 1
      warn "Warning: Could not fetch substantial documentation for #{@gem_name}"
      @sections << <<~MD
        ## Documentation Not Found

        Could not automatically fetch documentation. Try:

        1. Visit: https://github.com/#{@github_owner}/#{@github_repo}/wiki (if available)
        2. Visit: https://rubydoc.info/gems/#{@gem_name}
        3. Visit: https://rubygems.org/gems/#{@gem_name}
        4. Check gem homepage: `bundle info #{@gem_name}`
      MD
    end

    @sections << <<~MD

      ---
      *Generated by fetch-gem-docs.rb on #{Time.now.strftime("%Y-%m-%d %H:%M")}*
    MD

    File.write(@output_file, @sections.join("\n\n"))
  end
end

# Main execution
if ARGV.empty?
  puts "Usage: #{$PROGRAM_NAME} <gemname> [output_dir]"
  puts ""
  puts "Fetches comprehensive gem documentation including:"
  puts "  - GitHub Wiki pages (full documentation)"
  puts "  - agent-context files (AI-ready docs)"
  puts "  - README and examples"
  puts "  - YARD API docs"
  puts ""
  puts "Examples:"
  puts "  #{$PROGRAM_NAME} http"
  puts "  #{$PROGRAM_NAME} sidekiq doc/gems"
  puts "  #{$PROGRAM_NAME} ruby_llm ~/project/doc/gems"
  exit 1
end

gem_name = ARGV[0]
output_dir = ARGV[1]

GemDocsFetcher.new(gem_name, output_dir).call
