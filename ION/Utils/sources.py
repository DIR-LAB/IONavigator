import re

def remove_duplicate_sources(diagnosis_text, sources):
    # Dictionary to track unique sources and their new IDs
    source_contents = []
    unique_sources = {}
    new_sources = {}

    # Iterate over the sources to identify duplicates
    for source_id, source_content in sources.items():
        source_id_num = int(source_id.split(" ")[1])
        source_text = source_content["text"]
        if source_text not in source_contents:
            source_contents.append(source_text)
            unique_sources[source_text] = source_id_num
            new_sources[f"Source {source_id_num}"] = source_content

        else:
            new_source_id = unique_sources[source_text]
            diagnosis_text = re.sub(rf"\[{source_id_num}\]", f"[{new_source_id}]", diagnosis_text)
    # reset source ids so they are sequential and replace the old source ids with the new ones in the diagnosis text
    blank_new_sources = {}
    keys = list(new_sources.keys())
    for i, source in enumerate(keys):
        source_id = source.split(" ")[1]
        new_source_id = f"{i+1}"
        diagnosis_text = re.sub(rf"\[{source_id}\]", f"[{new_source_id}]", diagnosis_text)
        blank_new_sources[f"Source {new_source_id}"] = new_sources[source]
        del new_sources[source]
    new_sources = blank_new_sources


    return diagnosis_text, new_sources

def recalibrate_source_ids(diagnosis_text, sources):
    # recalibrate source ids
    new_sources = {}
    for i, source in enumerate(list(sources.keys())):
        source_id = source.split(" ")[1]
        new_source_id = f"{i+1}"
        diagnosis_text = re.sub(rf"\[{source_id}\]", f"[{new_source_id}]", diagnosis_text)
        new_sources[f"Source {new_source_id}"] = sources[source]
    diagnosis_text, new_sources = remove_duplicate_sources(diagnosis_text, new_sources)
    return diagnosis_text, new_sources


def extract_and_add_source_root(text_with_sources: str, root_id: int) -> str:
    # Define the pattern to match citations in the form of [id]
    pattern = r'\[(\d+(\.\d+)*)\]'
    
    # Define the replacement function
    def prepend_root(match):
        current_id = match.group(1)
        new_id = f"{root_id}.{current_id}"
        return f"[{new_id}]"
    
    # Replace all citations in the text
    updated_text = re.sub(pattern, prepend_root, text_with_sources)
    
    return updated_text

def prepend_source_key_with_root(sources: dict, root_id: int) -> dict:
    updated_sources = {}
    for key in sources:
        # each key is "Source X" where X is an integer
        source_id = key.split(" ")[1]
        new_key = f"Source {root_id}.{source_id}"
        updated_sources[new_key] = sources[key]
    return updated_sources


def extract_sources_from_text(text: str) -> dict:
    # Define the pattern to match citations in the form of [id]
    pattern = r'\[(\d+(\.\d+)*)\]'
    
    # Find all citations in the text
    matches = re.findall(pattern, text)
    
    # create a list of sources
    sources = set()
    
    # Iterate over the matches
    for match in matches:
        source_id = match[0]
        sources.add(source_id)

    return list(sources)

def remove_erroneous_sources(merged_summary, erroneous_sources):
    for source in erroneous_sources:
        try:
            merged_summary = re.sub(rf"\[{source}\]", "", merged_summary)
        except Exception as e:
            print(f"Error in remove_erroneous_sources for {source}")
            raise e
    return merged_summary


def create_merged_sources(sources1: dict, sources2: dict, sources_used: list) -> dict:
    merged_sources = {}
    erroneous_sources = []
    for source in sources_used:
        try:
            source_origin = source.split(".")[0]
            source_id = source.split(".")[1]
            try:
                if source_origin == "1":
                    merged_sources[f"Source {source}"] = sources1[f"Source {source_id}"]
                elif source_origin == "2":
                    merged_sources[f"Source {source}"] = sources2[f"Source {source_id}"]
            except KeyError:
                # source not found in either sources1 or sources2
                erroneous_sources.append(source)
        except Exception as e:
            print(f"Source {source} not found in sources1 or sources2")
            print(f"sources1: {sources1}")
            print(f"sources2: {sources2}")
            print(f"sources1 keys: {sources1.keys()}")
            print(f"sources2 keys: {sources2.keys()}")
            print(f"source searched: {source}")
            print(f"source_origin: {source_origin}")
            print(f"source_id: {source_id}")
            print(f"sources_used: {sources_used}")
            raise e
    return merged_sources, erroneous_sources

    