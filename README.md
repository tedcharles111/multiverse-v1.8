# Multiverse AI Web Builder

A powerful AI-powered web builder that creates complete, professional websites from simple descriptions. Built on GPT-Engineer with enhanced web development capabilities and free DeepSeek/Qwen models.

[![GitHub Repo stars](https://img.shields.io/github/stars/gpt-engineer-org/gpt-engineer?style=social)](https://github.com/gpt-engineer-org/gpt-engineer)
[![Discord Follow](https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat)](https://discord.gg/8tcDQ89Ej2)
[![License](https://img.shields.io/github/license/gpt-engineer-org/gpt-engineer)](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/LICENSE)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/gpt-engineer-org/gpt-engineer)](https://github.com/gpt-engineer-org/gpt-engineer/issues)
![GitHub Release](https://img.shields.io/github/v/release/gpt-engineer-org/gpt-engineer)
[![Twitter Follow](https://img.shields.io/twitter/follow/antonosika?style=social)](https://twitter.com/antonosika)

## 🚀 Multiverse AI Web Builder

A next-generation AI web builder inspired by Lovable AI, featuring a complete IDE experience with live preview, agentic reasoning, and powerful code generation capabilities.

### ✨ Key Features

- **Full IDE Experience**: Complete code editor with syntax highlighting and live preview
- **Agentic Reasoning**: AI explains its thinking process in real-time
- **Dual View Mode**: Switch between code editor and live preview instantly
- **Manual & AI Editing**: Edit code manually or through natural language prompts
- **Professional Templates**: Business, portfolio, e-commerce, and more
- **Responsive Design**: Mobile-first, works on all devices
- **Modern Tech Stack**: HTML5, CSS3, JavaScript with best practices
- **Project Management**: Save, load, and manage multiple projects
- **File Management**: Create, edit, and delete files seamlessly
- **Free AI Models**: Uses DeepSeek and Qwen models via OpenRouter
- **Open in New Tab**: Preview your website in a separate window

### 🤖 AI Models & Fallbacks

This project uses free models via OpenRouter with intelligent fallbacks:

**Primary Model:**
- `deepseek/deepseek-r1-0528:free` (128k context, 1800 max tokens)

**Fallback Models:**
- **Reasoning**: `qwen/qwen3-30b-a3b:free` (131k context)
- **Coding**: `qwen/qwen-2.5-coder-32b-instruct:free` (128k context)
- **Final**: `qwen/qwen3-coder:free` (128k context)

**Setup:**
1. Create an [OpenRouter account](https://openrouter.ai)
2. Copy your API key
3. Set `OPENROUTER_KEY` in your environment variables or use the provided key

### 🌐 Web Builder Interface

The Multiverse AI Web Builder features:

**Left Sidebar:**
- **AI Reasoning Panel**: See how the AI thinks and plans
- **Prompt Input**: Describe changes in natural language
- **File Explorer**: Manage project files with create/delete functionality

**Main Area:**
- **Code Editor**: Full-featured IDE with syntax highlighting
- **Live Preview**: Real-time preview of your website
- **Tab Management**: Work with multiple files simultaneously

**Header Controls:**
- **Save Project**: Persist your work
- **New Project**: Start fresh projects
- **Open Preview**: View in new tab

### 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r web-ui/requirements.txt
   ```

2. **Set Environment Variables:**
   ```bash
   export OPENROUTER_KEY=your_api_key_here
   ```

3. **Start the Web Builder:**
   ```bash
   python web-ui/app.py
   ```

4. **Open Browser:**
   Navigate to `http://localhost:3000`

### 💡 Usage Examples

**Create a New Website:**
```
Create a modern portfolio website for a photographer with:
- Dark theme with purple accents
- Hero section with background image
- Gallery grid for photos
- About section
- Contact form
- Smooth animations
```

**Modify Existing Code:**
```
Add a navigation menu to the header with smooth scrolling
Change the color scheme to blue and green
Add a footer with social media links
```

### 🛠️ Technical Features

- **Smart Model Selection**: Automatically chooses the best model for each task
- **Context Management**: Handles large codebases within token limits
- **Error Recovery**: Graceful fallbacks when models are unavailable
- **Real-time Updates**: Live preview updates as you type
- **Project Persistence**: Save and restore complete projects
- **File Management**: Full CRUD operations on project files

### 🎯 Architecture

```
Frontend (HTML/CSS/JS) → Flask Backend → OpenRouter API → DeepSeek/Qwen Models
                     ↓
                GPT Engineer Core → Enhanced Web Prompts → Generated Code
```

gpt-engineer lets you:
- Specify software in natural language
- Sit back and watch as an AI writes and executes the code
- Ask the AI to implement improvements

## Getting Started

### Install gpt-engineer

For **stable** release:

- `python -m pip install gpt-engineer`

For **development**:
- `git clone https://github.com/gpt-engineer-org/gpt-engineer.git`
- `cd gpt-engineer`
- `poetry install`
- `poetry shell` to activate the virtual environment

We actively support Python 3.10 - 3.12. The last version to support Python 3.8 - 3.9 was [0.2.6](https://pypi.org/project/gpt-engineer/0.2.6/).

### Setup API key

Choose **one** of:
- Export env variable (you can add this to .bashrc so that you don't have to do it each time you start the terminal)
    - `export OPENAI_API_KEY=[your api key]`
- .env file:
    - Create a copy of `.env.template` named `.env`
    - Add your OPENAI_API_KEY in .env
- Custom model:
    - See [docs](https://gpt-engineer.readthedocs.io/en/latest/open_models.html), supports local model, azure, etc.

Check the [Windows README](./WINDOWS_README.md) for Windows usage.

**Other ways to run:**
- Use Docker ([instructions](docker/README.md))
- Do everything in your browser:
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/gpt-engineer-org/gpt-engineer/codespaces)

### Create new code (default usage)
- Create an empty folder for your project anywhere on your computer
- Create a file called `prompt` (no extension) inside your new folder and fill it with instructions
- Run `gpte <project_dir>` with a relative path to your folder
  - For example: `gpte projects/my-new-project` from the gpt-engineer directory root with your new folder in `projects/`

### Improve existing code
- Locate a folder with code which you want to improve anywhere on your computer
- Create a file called `prompt` (no extension) inside your new folder and fill it with instructions for how you want to improve the code
- Run `gpte <project_dir> -i` with a relative path to your folder
  - For example: `gpte projects/my-old-project -i` from the gpt-engineer directory root with your folder in `projects/`

### Benchmark custom agents
- gpt-engineer installs the binary 'bench', which gives you a simple interface for benchmarking your own agent implementations against popular public datasets.
- The easiest way to get started with benchmarking is by checking out the [template](https://github.com/gpt-engineer-org/gpte-bench-template) repo, which contains detailed instructions and an agent template.
- Currently supported benchmark:
  - [APPS](https://github.com/hendrycks/apps)
  - [MBPP](https://github.com/google-research/google-research/tree/master/mbpp)

The community has started work with different benchmarking initiatives, as described in [this Loom](https://www.loom.com/share/206805143fbb4302b5455a5329eaab17?sid=f689608f-8e49-44f7-b55f-4c81e9dc93e6) video.

### Research
Some of our community members have worked on different research briefs that could be taken further. See [this document](https://docs.google.com/document/d/1qmOj2DvdPc6syIAm8iISZFpfik26BYw7ZziD5c-9G0E/edit?usp=sharing) if you are interested.

## Terms
By running gpt-engineer, you agree to our [terms](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/TERMS_OF_USE.md).


## Relation to gptengineer.app (GPT Engineer)
[gptengineer.app](https://gptengineer.app/) is a commercial project for the automatic generation of web apps.
It features a UI for non-technical users connected to a git-controlled codebase.
The gptengineer.app team is actively supporting the open source community.


## Features

### Pre Prompts
You can specify the "identity" of the AI agent by overriding the `preprompts` folder with your own version of the `preprompts`. You can do so via the `--use-custom-preprompts` argument.

Editing the `preprompts` is how you make the agent remember things between projects.

### Vision

By default, gpt-engineer expects text input via a `prompt` file. It can also accept image inputs for vision-capable models. This can be useful for adding UX or architecture diagrams as additional context for GPT Engineer. You can do this by specifying an image directory with the `—-image_directory` flag and setting a vision-capable model in the second CLI argument.

E.g. `gpte projects/example-vision gpt-4-vision-preview --prompt_file prompt/text --image_directory prompt/images -i`

### Open source, local and alternative models

By default, gpt-engineer supports OpenAI Models via the OpenAI API or Azure OpenAI API, as well as Anthropic models.

With a little extra setup, you can also run with open source models like WizardCoder. See the [documentation](https://gpt-engineer.readthedocs.io/en/latest/open_models.html) for example instructions.

## Mission

The gpt-engineer community mission is to **maintain tools that coding agent builders can use and facilitate collaboration in the open source community**.

If you are interested in contributing to this, we are interested in having you.

If you want to see our broader ambitions, check out the [roadmap](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/ROADMAP.md), and join
[discord](https://discord.gg/8tcDQ89Ej2)
to learn how you can [contribute](.github/CONTRIBUTING.md) to it.

gpt-engineer is [governed](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/GOVERNANCE.md) by a board of long-term contributors. If you contribute routinely and have an interest in shaping the future of gpt-engineer, you will be considered for the board.

## Significant contributors
<ul style="list-style-type: none; padding: 0; display: flex; flex-wrap: wrap;"> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/ATheorell"> <img src="https://avatars.githubusercontent.com/u/143704446?s=64&v=4" alt="@ATheorell" width="32" height="32" style="border-radius: 50%;"> @ATheorell </a> </li> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/similato87"> <img src="https://avatars.githubusercontent.com/u/71301573?s=64&v=4" alt="@similato87" width="32" height="32" style="border-radius: 50%;"> @similato87 </a> </li> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/TheoMcCabe"> <img src="https://avatars.githubusercontent.com/u/9841960?s=64&v=4" alt="@TheoMcCabe" width="32" height="32" style="border-radius: 50%;"> @TheoMcCabe </a> </li> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/captivus"> <img src="https://avatars.githubusercontent.com/u/366332?s=64&v=4" alt="@captivus" width="32" height="32" style="border-radius: 50%;"> @captivus </a> </li> </ul>


## Example



https://github.com/gpt-engineer-org/gpt-engineer/assets/4467025/40d0a9a8-82d0-4432-9376-136df0d57c99