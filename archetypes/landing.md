---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
layout: "landing"
description: ""

# Landing page sections — controls which section partials are rendered
# Available sections: hero, capabilities, process, specification,
#   materials, industries, certifications, faq, rfq
sections:
  - hero
  - capabilities
  - process
  - faq
  - rfq

# Schema configuration (optional)
# schema:
#   faq:
#     - question: "What is your question?"
#       answer: "Here is the answer."
#     - question: "Another question?"
#       answer: "Another answer."
---

