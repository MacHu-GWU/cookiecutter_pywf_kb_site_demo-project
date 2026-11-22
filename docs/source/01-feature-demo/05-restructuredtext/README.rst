:doc_id: OAFSttVJviBK
:description: Explains how old reStructuredText documents live next to MyST documents and link to them. A reST compatibility demo.

reStructuredText Document
==============================================================================
Old documents need no migration. A reST document keeps its doc_id in the field list at the very top of the file (Sphinx calls it docinfo).

Linking to MyST documents
------------------------------------------------------------------------------
- A whole document: :ref:`bhNtpbPvxMCO`
- A section: :ref:`bhNtpbPvxMCO-cross-ref`
- Custom text: :ref:`a document four levels deep <tPLKDkIdEbXW>`

mermaid
------------------------------------------------------------------------------
.. mermaid::

    flowchart TD
        rst[README.rst] --> sphinx[Sphinx]
        md[README.md] --> sphinx

sphinx-design
------------------------------------------------------------------------------
.. grid:: 2

    .. grid-item-card:: reST card A

        Content A

    .. grid-item-card:: reST card B

        Content B
