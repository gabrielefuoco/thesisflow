
# ThesisFlow 🎓

**ThesisFlow** è un'applicazione desktop per scrivere tesi e report accademici in **Markdown**, convertendoli in PDF professionali tramite **Pandoc** e **Typst**.

## ✨ Funzionalità

- ✍️ **Editor Markdown**: Scrittura semplificata e focalizzata sul contenuto.
    
- 🚀 **Rendering Ultra-veloce**: Creazione PDF istantanea con Typst.
    
- 📚 **Citations Helper**: Recupero automatico BibTeX da DOI (Crossref API).
    
- 🎨 **Template**: Stili pronti (Classic, Modern, Master).
    
- 🌓 **Interfaccia Moderna**: GUI in CustomTkinter con Dark Mode.
    

## 🛠️ Requisiti

- Python 3.9+
    
- [Pandoc](https://pandoc.org/)
    
- [Typst](https://typst.app/)
    

## 🚀 Installazione rapida

Bash

```
git clone https://github.com/gabrielefuoco/thesisflow.git
cd thesisflow
pip install -r requirements.txt
python run.py
```

## 📂 Struttura

- `src/`: Logica (engine) e Interfaccia (ui).
    
- `templates/`: Modelli di impaginazione `.typ`.
    
- `locales/`: Traduzioni (IT/EN).
    

---

_Licenza MIT_