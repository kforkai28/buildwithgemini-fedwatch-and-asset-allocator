"""A2UI Schema Prompt generator for FedWatch & Asset Allocator."""

A2UI_INSTRUCTION_APPENDIX = """
### A2UI Rich UI Format Guidelines (v0.8):
When the user asks for a summary, portfolio model, Treasury yield digest, or infographic, return an A2UI JSON array along with your response so adk web can render it visually.

Rules for A2UI:
1. Keep surfaces flat: ONE Card > ONE Column > a few Text, Row, or Image components. Never nest a Card inside a Card.
2. Supported components: Card, Column, Row, Text, Divider, Image.
3. For images: If you generated an image with `generate_macro_infographic`, use an Image component with the exact public HTTPS url:
   {"id": "chart_img", "component": {"Image": {"url": {"literalString": "https://storage.googleapis.com/..."}, "alt": {"literalString": "Macro Chart"}}}}
4. Do not use Table or Heading components. For tables, build them from Rows with Text components.
5. In Text components, use `usageHint`: 'h1', 'h2', or 'body' for formatting.
6. When emitting A2UI, output the raw JSON array (containing `beginRendering` and `surfaceUpdate` objects).

Example A2UI JSON:
[
  {
    "beginRendering": {
      "surfaceId": "macro_card",
      "root": "main_card"
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "macro_card",
      "components": [
        {
          "id": "main_card",
          "component": {
            "Card": {
              "child": "main_col"
            }
          }
        },
        {
          "id": "main_col",
          "component": {
            "Column": {
              "children": {
                "explicitList": ["title", "divider1", "stat_row"]
              }
            }
          }
        },
        {
          "id": "title",
          "component": {
            "Text": {
              "text": {"literalString": "FedWatch Macro Overview"},
              "usageHint": "h1"
            }
          }
        },
        {
          "id": "divider1",
          "component": {
            "Divider": {}
          }
        },
        {
          "id": "stat_row",
          "component": {
            "Row": {
              "children": {
                "explicitList": ["stat_label", "stat_val"]
              }
            }
          }
        },
        {
          "id": "stat_label",
          "component": {
            "Text": {
              "text": {"literalString": "10Y Treasury: "},
              "usageHint": "body"
            }
          }
        },
        {
          "id": "stat_val",
          "component": {
            "Text": {
              "text": {"literalString": "5.10% (Normal Slope)"},
              "usageHint": "body"
            }
          }
        }
      ]
    }
  }
]
"""
