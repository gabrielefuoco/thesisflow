
// Modern Report Template

#import ".thesis_data/temp/metadata.typ": *

#set document(title: title, author: author)
#set page(
  paper: "a4", 
  margin: (x: 3cm, y: 3cm),
  numbering: "1"
)
#set text(
  font: "Arial", 
  size: 11pt,
  lang: "it"
)
#set par(
  justify: true, 
  leading: 0.65em
)

// Branding / Color
#let primary_color = rgb("#0055aa")

#show heading: it => [
  #set text(fill: primary_color)
  #block(above: 1.5em, below: 1em, it)
]
#set heading(numbering: "1.1")

// Title Page
#align(center + horizon)[
  #rect(fill: primary_color, width: 100%, height: 4em, radius: 1em)[
    #align(center + horizon)[
      #text(fill: white, 2em, weight: "bold")[#title]
    ]
  ]
  
  #v(3em)
  
  #text(1.5em, weight: "bold")[#candidate]
  #v(1em)
  Relatore: #supervisor
  
  #v(2em)
  #year
]

#pagebreak()

// TOC
#outline(indent: auto)
#pagebreak()

// Body
#include ".thesis_data/temp/compiled_body.typ"
