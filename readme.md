# PDF Structural Parser
Most libraries extract text as it is from PDF documents, but ignore the given natural order like chapters, sections and subsections. 
`pdfstructure` parses and stores the relations between paragraphs in a nested tree structure. 


```
    Header: Chapter 1                   << H1 Header Font >>
    Content:                            << Body Font >>
        Header: Section 1.1             << H2 Header Font >>
        Content:                        << Body Font >>
        Header: Section 1.2             << H2 Header Font >>
        Content:                        << Body Font >>
            Header: Subsection 1.2.1    << H3 Header Font >>
            Content:                    << Body Font >>
    Header: Chapter 2                   << H1 Header Font >>
    content:                            << Body Font >>
```


## Parse PDF with natural order

```
# specify source (that implements source.read())
source = FileSource(path)   
# analyse document and parse as nested data structure
pdf = parser.parse_pdf(source)
```

### Get Pretty String Text
To export the parsed structure, use a printer implementation.
```
stringExporter = PrettyStringPrinter()

prettyString = stringExporter.print(pdf)
```
```
# excerpt of the example string looks like:

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

### Serialize PDF to JSON
```
    printer = JsonFilePrinter()

    file_path = Path("resources/parsed/interview_cheatsheet.json")
    printer.print(self.testDocument, file_path=str(file_path.absolute()))
```

Excerpt of exported json:
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
                "level": 0,
                "text": "Data Structure Basics"
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
                        "level": 0,
                        "metadata": {
                            "page": 0
                        },
                        "text": "Array"
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
                                "level": 0,
                                "text": "Definition:"
                            },
                            "content": [
                                {
                                    "style": {
                                        "bold": false,
                                        "italic": false,
                                        "font_name": ".SFNSText",
                                        "mapped_font_size": "middle",
                                        "mean_size": 8.5
                                    },
                                    "level": 2,
                                    "text": "Stores data elements based on an sequential, most commonly 0 based, index."
                                }
                            ]}
            ]
}
          
```



## Applications
* Search Engines: Index and make document searchable on a per paragraph basis. 
  * Custom scoring functions
    * match on title vs sub title, content on a lower nested level
    
* Extract a useful name for documents, when the original filename is not meaningful.