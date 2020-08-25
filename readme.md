# PDF Structural Parser
`pdfstructure` detects, splits and organises the documents text content into its natural structure as envisioned by the author.
The document structure, or hierarchy, stores the relation between chapters, sections and their sub sections in a nested, recursive manner.   


`pdfstructure` is in early development and built on top of [pdfminer.six](https://github.com/pdfminer/pdfminer.six). 

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

```
# specify source (that implements source.read())
source = FileSource(path)   
# analyse document and parse as nested data structure
pdf = parser.parse_pdf(source)
```

### Serialize Document to String
To export the parsed structure, use a printer implementation.
```
stringExporter = PrettyStringPrinter()

prettyString = stringExporter.print(pdf)
```

**Excerpt of the parsed document (serialized to string)**
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

### Serialize Document to JSON
```
    printer = JsonFilePrinter()

    file_path = Path("resources/parsed/interview_cheatsheet.json")
    printer.print(self.testDocument, file_path=str(file_path.absolute()))
```

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
