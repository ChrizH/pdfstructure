# PDF Structural Parser
`pdfstructure` detects, splits and organises the documents text content into its natural structure as envisioned by the author.
The document structure, or hierarchy, stores the relation between chapters, sections and their sub sections in a nested, recursive manner.   


`pdfstructure` is in early development and built on top of [pdfminer.six](https://github.com/pdfminer/pdfminer.six). 

- Paragraph extraction is performed leveraging `pdfminer.high_level.extract_pages()`.
- Those paragraphs are then grouped together according to some basic (extendable) heuristics.

## Document Model

```
class StructuredDocument:
  metadata: dict
  sections: List[Section]

class Section:
  content:  TextElement
  children: List[Section]
  level:    int

class TextElement:
  text:     LTTextContainer # the extracted paragraph from pdfminer
  style:    Style
```

## Load and parse PDF

**Illustration of document structure**

The following screenshot contains sections and subsections with their respective content. 
In that case, the structure can be easily parsed by leveraging the Font Style only.

![Example PDF](tests/resources/interview_cheatsheet-excerpt.png?raw=true)
*PDF source: [github.com/TSiege](https://gist.github.com/TSiege/cbb0507082bb18ff7e4b)*


**Parse PDF**
```
    from pdfstructure.hierarchy.parser import HierarchyParser
    from pdfstructure.source import FileSource

    parser = HierarchyParser() 
    
    # specify source (that implements source.read())
    source = FileSource(path) 
     
    # analyse document and parse as nested data structure
    document = parser.parse_pdf(source)
```

### Serialize Document to String
To export the parsed structure, use a printer implementation.
```
    from pdfstructure.printer import PrettyStringPrinter

    stringExporter = PrettyStringPrinter()
    prettyString = stringExporter.print(document)
```

**Excerpt of the parsed document (serialized to string)**

[Parsed data: interview_cheatsheet_pretty.txt](tests/resources/parsed/interview_cheatsheet_pretty.txt?raw=true)
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
    from pdfstructure.printer import JsonFilePrinter
    
    printer = JsonFilePrinter()
    file_path = Path("resources/parsed/interview_cheatsheet.json")
    
    printer.print(document, file_path=str(file_path.absolute()))
```

[Parsed data: interview_cheatsheet.json](tests/resources/parsed/interview_cheatsheet.json?raw=true)

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
            "content": {
                "style": {
                    "bold": true,
                    "italic": false,
                    "font_name": ".SFNSDisplay-Semibold",
                    "mapped_font_size": "xlarge",
                    "mean_size": 12.8,
                    "max_size": 12.806323818403143
                },
                "page": 0,
                "text": "Data Structure Basics"
            },
            "children": [
                {
                    "content": {
                        "style": {
                            "bold": true,
                            "italic": false,
                            "font_name": ".SFNSDisplay-Semibold",
                            "mapped_font_size": "large",
                            "mean_size": 10.6,
                            "max_size": 10.671936515335972
                        },
                        "page": 0,
                        "text": "Array"
                    },
                    "children": [
                        {
                            "content": {
                                "style": {
                                    "bold": true,
                                    "italic": false,
                                    "font_name": ".SFNSText-Semibold",
                                    "mapped_font_size": "middle",
                                    "mean_size": 8.5,
                                    "max_size": 8.537549212268772
                                },
                                "page": 0,
                                "text": "Definition:"
                            },
         ....          
```


### Load JSON as StructuredPdfDocument

Of course, encoded documents can be easily decoded and used for further analysis. 
However, detailed information like bounding boxes or coordinates for each character are not persisted.

```
    from pdfstructure.model.document import StructuredPdfDocument

    jsonString = json.load(file)
    document = StructuredPdfDocument.from_json(jsonString)
    
    print(document.title)
``
        $ "interview_cheatsheet.pdf"
```

## Traverse through document structure
Having all paragraphs and sections organised as a general tree, 
its straight forward to iterate through the layers and search for specific elements like headlines, or extract all main headers like chapter titles.  

Two document traversal generators are available that yield each section `in-order` or in `level-order` respectively. 
```
    from pdfstructure.hierarchy.traversal import traverse_in_order

    elements_flat_in_order = [element for element in traverse_in_order(document)]

    Exemplary illustration of yield order:
        """
                         5   10
                      /   \    \
                     1     2    3
                   / | \        |
                  a  b  c       x
    
        yield order:
        - [5,1,a,b,c,2,10,3,x]
        """
```


# TODOs
- [ ] **Detect the document layout type (Columns, Book, Magazine)**
    
    The provided layout analysis algorithm by pdfminer.six performs well on more straightforward documents with default settings. 
    However, more complicated layouts like scientific papers need custom `LAParams` settings to retrieve paragraphs in correct reading order.
- [ ] High level diagram of algorithm workflow
- [ ] Performance improvement in terms of speed