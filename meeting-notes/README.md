# Meeting Notes

## 2023-07-19

### Preliminaries

#### Frameworks Related to LLMs

- OpenAI
- Langchain
  - basic usages
    - prompt templates
    - OpenAI LLMs
  - `memory` module
  - `agents` module
- BabyAGI
  - workflow architecture 

#### Databases

- PostgreSQL
  - Docker
  - GUI editor: PgAdmin, DBeaver
  - CRUD: Create, Read, Update and Delete
  - Python client: Psycopg
- MongoDB
  - GUI editor: MongoDB Compass
  - CRUD
  - Python client: `pymongo`
- Qdrant
  - Docker
  - Python client: `qdrant-client`
- Pgvector
  - It is an extension for PostgreSQL database
  - Python client: `pgvector-python`

### Python Programming Style Guidelines 

#### Naming Conventions

- Module
  - Snake case (It needs to be short and better not to have underscores `_`)
  - e.g.,  `numpy`, `sklearn`
  - But underscores are also acceptable
    - e.g.,  `chat_models`
    - Usually, modules with underscores are private ones
- Variables
  - Snake case
- Functions and Methods
  - Snake case
- Classes
  - Camel case
  - e.g., `class MyAgent`
- Macros or Global Variables 
  - Upper case
  - e.g., `OPENAI_API_KEY`, `DATA_DIR`

#### Private Class Attributes

- No class attributes are really private in Python
- By convention, we use one underscore prefix for a private attribute. e.g., `self._database_name = "test_db"`

#### Properties

- Learn to use properties. Use `@property` to decorate some class attributes.
- Getter
- Setter


#### Type Annotations

- Common Data Types

- Optional Variables
  - Variables that may be `None`
  - e.g.,
  ```py
  from typing import Optional

  text: Optional[str] = None 
  ```

- In Function Signatures
  - Parameter type
  - Return type
  - e.g.
  ```py
  from typing import Optional

  def get_response(
        query: str, 
        temperature: float = 0.0
    ) -> Optional[str]:
    ...
  ```


#### Docstring

- Numpy style
- VS Code Extension: `autoDocstring - Python Docstring Generator`

#### Integration Tests

- Built-in `unittest` package

### Coding Tasks

#### Chat GPT Replica with Langchain

Use Langchain to create your own chat GPT with context awareness. 

The appearance of your program is immaterial. CLI, GUI or web app are all fine.

The goal is to get familiar with Langchain package, and understand the underlying mechanism of its memory buffer.

Hints:
- Conversation buffer memory
- `streamlit`


### Tasks

- Be familiar with:
  - CoT: Chain of Thoughts
  - ReAct
  - Reflexion
  - Domain knowledge with vector database
- Search for benchmark datasets
  - Prove that our implementation performs better than others
  - Q&As
- How to provide better answers with up-to-date information using Google 
- Selection and summary of short-term conversational memory
Leverage other open-source LLMs
- Teach LLM to use APIs
  - Machine learning models (Scikit-Learn)
  - Plottings (Matplotlib)
- Investigate how knowledge graph can be integrated into LLM

