import json
import re
import os
from html import escape
import html
import markdown2
import asyncio
from ION.Prompts import format_simple_prompt
from ION.Completions import generate_async_completion
from ION.Utils import get_root_path, get_path, setup_logger
from ION.Steps.Utils import FINAL_DIAGNOSIS_DIR, FINAL_DIAGNOSIS_NAME

output_refinement_logger = setup_logger("output_refinement")

def md_to_html(md_content):
    output_refinement_logger.info("Converting markdown to HTML")
    def format_json(match):
        try:
            # Parse the JSON
            json_obj = json.loads(match.group(1).replace("'", '"'))
            # Format it with indentation
            formatted_json = json.dumps(json_obj, indent=2)
            # Wrap it in a code block
            return f"\n```json\n{formatted_json}\n```\n"
        except json.JSONDecodeError:
            # If it's not valid JSON, return it unchanged
            return match.group(0)
    
    # Find and format JSON content within <json> tags
    md_content = re.sub(r'<json>(.*?)</json>', lambda m: f"{format_json(m)}", md_content, flags=re.DOTALL)
    
    # Escape underscores in method names and identifiers
    escaped_content = re.sub(r'(\w+)_(\w+)', r'\1\\_\2', md_content)
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(escaped_content, safe_mode='escape', extras=['fenced-code-blocks'])
    
    # Unescape the underscores in the HTML content
    final_html = html_content.replace('\\_', '_')
    
    return final_html

def json_to_html(diagnosis_dict):
    output_refinement_logger.info("Converting JSON to HTML")
    summary = diagnosis_dict['diagnosis']
    sources = diagnosis_dict['sources']

    # Function to replace citations with tooltip spans
    def replace_citation(match):
        citation_num = match.group(1)
        source_key = f"Source {citation_num}"
        if source_key in sources:
            source = sources[source_key]
            source_file = source['file'].replace(".md", "")
            # Escape HTML characters and replace newlines with <br> tags
            tooltip_content = f"<span class='source-file'>{html.escape(source_file)}</span>: {html.escape(source['text'])}"
            tooltip_content = tooltip_content.replace('\n', '<br>') 
            # cases such as !6_image_0.png, '!' should be removed
            tooltip_content = re.sub(r'!(\d+)_image_\d+\.png', r'\1', tooltip_content)

            markdown_special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!']
            for char in markdown_special_chars:
                tooltip_content = tooltip_content.replace(char, '\\' + char)

            # Print the tooltip content for debugging
            print(f"Tooltip content: {tooltip_content}")
            
            return f'<span class="tooltip">[{citation_num}]<span class="tooltiptext">{tooltip_content}</span></span>'
        return match.group(0)
    
    summary_with_tooltips = re.sub(r'\[(\d+)\]', replace_citation, summary)
    html_summary = markdown2.markdown(summary_with_tooltips, safe_mode='escape')

    final_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Summary with Citations</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .tooltip {{
                    position: relative;
                    display: inline-block;
                    border-bottom: 1px dotted black;
                    cursor: pointer;
                }}
                .tooltip .tooltiptext {{
                    visibility: hidden;
                    width: auto;
                    max-width: 80vw; /* Maximum width of 80% of the viewport width */
                    white-space: normal;
                    word-wrap: break-word;
                    text-align: left;
                    padding: 10px;
                    position: fixed; /* Changed from absolute to fixed */
                    z-index: 2000;
                    opacity: 0;
                    transition: opacity 0.3s;
                    font-size: 12px; /* Smaller font size */
                    background-color: #f9f9f9; /* Light background color */
                    border: 1px solid #ccc; /* Border */
                    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); /* Shadow */
                    pointer-events: none; /* Prevent tooltip from blocking mouse events */
                }}
                .tooltip:hover .tooltiptext {{
                    visibility: visible;
                    opacity: 1;
                }}
                .source-file {{
                    font-weight: bold;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            {html_summary}
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var tooltips = document.querySelectorAll('.tooltip');
                    tooltips.forEach(function(tooltip) {{
                        var tooltiptext = tooltip.querySelector('.tooltiptext');
                        
                        tooltip.addEventListener('mousemove', function(e) {{
                            var x = e.clientX;
                            var y = e.clientY;
                            
                            tooltiptext.style.left = (x + 10) + 'px';  // 10px right of cursor
                            
                            // Increase the distance to the top which triggers the tooltip to be shown below the cursor
                            var topThreshold = 100; // Adjust this value as needed
                            if (y < topThreshold) {{
                                tooltiptext.style.top = (y + 20) + 'px';   // 20px below cursor
                            }} else {{
                                tooltiptext.style.top = (y - 10) + 'px';   // 10px above cursor
                            }}
                            
                            // Adjust if tooltip goes off-screen
                            var rect = tooltiptext.getBoundingClientRect();
                            if (rect.right > window.innerWidth) {{
                                tooltiptext.style.left = (window.innerWidth - rect.width - 10) + 'px';
                            }}
                            if (rect.bottom > window.innerHeight) {{
                                tooltiptext.style.top = (window.innerHeight - rect.height - 10) + 'px';
                            }}
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """
    output_refinement_logger.debug(f"Generated HTML summary with {len(sources)} sources")
    return html.unescape(final_html)

def format_diagnosis_html(config, diagnosis_dict=None):
    output_refinement_logger.info("Formatting diagnosis as HTML")
    root_path = get_root_path(config)
    # Read JSON file
    if diagnosis_dict:
        data = diagnosis_dict
        output_refinement_logger.debug("Using provided diagnosis_dict")
    else:
        json_file = get_path([root_path, FINAL_DIAGNOSIS_DIR, f"{FINAL_DIAGNOSIS_NAME}.json"])
        if json_file:
            with open(json_file, 'r') as f:
                data = json.load(f)
            output_refinement_logger.debug(f"Loaded JSON file: {json_file}")
        else:
            output_refinement_logger.error("Neither diagnosis_dict nor json_file provided")
            raise ValueError("'diagnosis_dict' or 'json_file' must be provided")

    html_summary = json_to_html(data)
    # Write HTML to file in the specified output directory
    output_file = os.path.join(root_path, 'final_diagnosis.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_summary)

    output_refinement_logger.info(f"HTML file generated: {output_file}")
    return output_file

async def format_diagnosis_md(config, final_diagnosis=None):
    output_refinement_logger.info("Formatting diagnosis as Markdown")
    root_path = get_root_path(config)
    if final_diagnosis is None:
        final_diagnosis_path = os.path.join(root_path, FINAL_DIAGNOSIS_DIR, f"{FINAL_DIAGNOSIS_NAME}.json")
        with open(final_diagnosis_path, "r") as f:
            data = json.load(f)
    else:
        data = final_diagnosis
    if "output_refinement" in config["steps"]:
        model = config["steps"]["output_refinement"]["model"]
    else:
        model = config["default_model"]
    output_refinement_logger.debug(f"Using model: {model}")

    diagnosis_content = data["diagnosis"]
    markdown_prompt = format_simple_prompt("format_markdown", {"diagnosis": diagnosis_content})
    output_refinement_logger.debug("Generating markdown content")
    markdown_content = await generate_async_completion(model, markdown_prompt)
    reformatted_diagnosis = {"diagnosis": markdown_content, "sources": data["sources"]}
    output_file = os.path.join(root_path, FINAL_DIAGNOSIS_DIR, f"md_formatted_{FINAL_DIAGNOSIS_NAME}.json")
    with open(output_file, "w") as f:
        json.dump(reformatted_diagnosis, f, indent=4)

    output_refinement_logger.info(f"Markdown-formatted diagnosis saved: {output_file}")
    return reformatted_diagnosis

if __name__ == "__main__":
    output_refinement_logger.info("Running output_refinement as main")
    default_config = json.load(open("/Users/chris/Documents/Github/IONPro/IONPro/Configs/default_config.json", "r"))
    format_diagnosis_html(default_config)
    output_refinement_logger.info("Output refinement completed")