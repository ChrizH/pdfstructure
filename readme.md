# PDF Structural Parser
`pdfstructure` detects, splits and organises the documents text content into its natural structure as envisioned by the author.
The document structure, or hierarchy, stores the relation between chapters, sections and their sub sections in a nested, recursive manner.   


`pdfstructure` is in early development and built on top of [pdfminer.six](https://github.com/pdfminer/pdfminer.six). 

- Paragraph extraction is performed leveraging `pdfminer.high_level.extract_pages()`.
- Those paragraphs are then grouped together according to some basic (extendable) heuristics.

## Document Model

```
# Document Representation with all sections
class StructuredPdfDocument:
    metadata: dict
    elements: List[Section]

# One Section
class Section:
    heading: TextElement
    content: List[TextElement]
    children: List[Section]
    
    # level denotes the nodes depth within tree structure 
    level: int  

# Group of words
class TextElement:
    text: str
    style: Style
    page: int
```

## Load and parse PDF

**Illustration of document structure**

The following screenshot contains sections and subsections with their respective content. 
In that case, the structure can be easily parsed by leveraging the Font Style only.

![https://gist.github.com/TSiege/cbb0507082bb18ff7e4b](tests/resources/interview_cheatsheet-excerpt.png?raw=true)
*PDF source: [github.com/TSiege](https://gist.github.com/TSiege/cbb0507082bb18ff7e4b)*


**Parse PDF**
```
    parser = HierarchyParser() 
    
    # specify source (that implements source.read())
    source = FileSource(path) 
     
    # analyse document and parse as nested data structure
    document = parser.parse_pdf(source)
```

### Serialize Document to String
To export the parsed structure, use a printer implementation.
```
    stringExporter = PrettyStringPrinter()

    prettyString = stringExporter.print(document)
```

**Excerpt of the parsed document (serialized to string)**

[Parsed data: interview_cheatsheet_pretty.txt](tests/resources/interview_cheatsheet_pretty.txt)
```
[Search Basics]
	[Breadth First Search]
		[Definition:]
			An algorithm that searches a tree (or graph) by searching levels of the tree first, starting at the root.
			It finds every node on the same level, most often moving left to right.
			While doing this it tracks the children nodes of the nodes on the current level.
			When finished examining a level it moves to the left most node on the next level.
			The bottom-right most node is evaluated last (the node that is deepest and is farthest right of it's level).

		[What you need to know:]
			Optimal for searching a tree that is wider than it is deep.
			Uses a queue to store information about the tree while it traverses a tree.
			Because it uses a queue it is more memory intensive than depth first search.
			The queue uses more memory because it needs to stores pointers
```

### Encode Document to JSON
```
    printer = JsonFilePrinter()

    file_path = Path("resources/parsed/interview_cheatsheet.json")
    
    printer.print(document, file_path=str(file_path.absolute()))
```

[Parsed data: interview_cheatsheet.json](tests/resources/interview_cheatsheet.json)

**Excerpt of exported json**
```
{
    "metadata": {
        "style_info": {
            "_data": {
                "7.99": 24,
                "9.6": 1,
                "6.4": 7,
                "7.47": 3,
                "12.8": 7,
                "8.53": 206,
                "10.67": 12,
                "7.25": 14
            },
            "_body_size": 8.53,
            "_min_found_size": 6.4,
            "_max_found_size": 12.8
        },
        "filename": "interview_cheatsheet.pdf"
    },
    "elements": [
       {
            "heading": {
                "style": {
                    "bold": true,
                    "italic": false,
                    "font_name": ".SFNSDisplay-Semibold",
                    "mapped_font_size": "xlarge",
                    "mean_size": 12.8
                },
                "page": 2,
                "text": "Search Basics"
            },
            "content": [],
            "children": [
                {
                    "heading": {
                        "style": {
                            "bold": true,
                            "italic": false,
                            "font_name": ".SFNSDisplay-Semibold",
                            "mapped_font_size": "large",
                            "mean_size": 10.6
                        },
                        "page": 2,
                        "text": "Breadth First Search"
                    },
                    "content": [],
                    "children": [
                        {
                            "heading": {
                                "style": {
                                    "bold": true,
                                    "italic": false,
                                    "font_name": ".SFNSText-Semibold",
                                    "mapped_font_size": "middle",
                                    "mean_size": 8.5
                                },
                                "page": 2,
                                "text": "Definition:"
                            },
         ....          
```


### Load JSON as StructuredPdfDocument

Of course, encoded documents can be easily decoded and used for further analysis. 
However, detailed information like bounding boxes or coordinates for each character are not persisted.

```
jsonString = json.load(file)
document = StructuredPdfDocument.from_json(jsonString)

print(document.title)
$ "interview_cheatsheet.pdf"
```


# TODOs
- [ ] **Detect the document layout type (Columns, Book, Magazine)**
    
    The provided layout analysis algorithm by pdfminer.six performs well on more straightforward documents with default settings. 
    However, more complicated layouts like scientific papers need custom `LAParams` settings to retrieve paragraphs in correct reading order.
- [ ] High level diagram of algorithm workflow