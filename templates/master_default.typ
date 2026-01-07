
// Master Template Default
#import ".thesis_data/temp/metadata.typ": *

#set page(
  paper: "a4",
  margin: (inside: 3cm, outside: 2cm, y: 2cm),
)

#set text(
  font: "Times New Roman",
  size: 12pt,
  lang: "it"
)

#set par(
  justify: true,
  leading: 0.65em,
  first-line-indent: 1.5em
)

// --- Front Page ---
#v(1fr)
#align(center)[
  #text(size: 24pt, weight: "bold")[#title]
  
  #v(2cm)
  
  #text(size: 16pt)[Tesi di Laurea]
  
  #v(2cm)
  #grid(
    columns: (1fr, 1fr),
    align(left)[
      *Candidato:*\
      #candidate
    ],
    align(right)[
      *Relatore:*\
      #supervisor
    ]
  )
  
  #v(1fr)
  #text(size: 14pt)[Anno Accademico #year]
]
#pagebreak()
// ----------------

#set page(numbering: "1")
#counter(page).update(1)

// Include the compiled body from Pandoc
#include ".thesis_data/temp/compiled_body.typ"
