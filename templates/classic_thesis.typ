
// Classic Thesis Template

#import ".thesis_data/temp/metadata.typ": *

#set document(title: title, author: author)
#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 2.5cm),
  numbering: "1",
)
#set text(
  font: "Times New Roman", 
  size: 12pt,
  lang: "it"
)
#set par(
  justify: true, 
  leading: 0.8em,
  first-line-indent: 1.5em
)

// Headings
#show heading: set block(above: 1.4em, below: 1em)
#set heading(numbering: "1.1")

// Title Page
#align(center + horizon)[
  #text(2em, weight: "bold")[#title]
  
  #v(2em)
  
  #text(1.2em)[Candidato: #candidate]
  #v(1em)
  #text(1.2em)[Relatore: #supervisor]
  
  #v(4em)
  #text(1.2em)[Anno Accademico #year]
]

#pagebreak()

// TOC
#outline(depth: 3, indent: true)
#pagebreak()

// Body
#include ".thesis_data/temp/compiled_body.typ"
