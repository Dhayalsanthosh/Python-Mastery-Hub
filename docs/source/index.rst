.. File: docs/source/index.rst

Python Mastery Hub Documentation
=================================

Welcome to Python Mastery Hub, an interactive learning platform designed to help you master Python programming through hands-on exercises, comprehensive tutorials, and real-world projects.

.. image:: ../assets/images/logo.png
   :alt: Python Mastery Hub Logo
   :align: center
   :width: 200px

.. note::
   This documentation is for Python Mastery Hub v1.0.0. For the latest updates and features, 
   please visit our `GitHub repository <https://github.com/python-mastery-hub/python-mastery-hub>`_.

What is Python Mastery Hub?
----------------------------

Python Mastery Hub is a comprehensive learning platform that provides:

🎯 **Interactive Learning Environment**
   - Browser-based Python code editor with syntax highlighting
   - Real-time code execution and testing
   - Instant feedback on exercises and challenges

📚 **Structured Learning Path**
   - Beginner to advanced Python concepts
   - Hands-on exercises and projects
   - Progress tracking and achievements

🧪 **Practical Application**
   - Real-world coding challenges
   - Industry-standard practices
   - Portfolio-worthy projects

🌐 **Web-Based Platform**
   - No installation required
   - Cross-platform compatibility
   - Collaborative learning features

Quick Start
-----------

Get started with Python Mastery Hub in minutes:

1. **Installation**::

   pip install python-mastery-hub

2. **Start the Web Server**::

   pmh web start

3. **Open your browser** and navigate to http://localhost:8000

4. **Begin learning** with our interactive tutorials!

Key Features
------------

**For Learners**
   - Interactive Python tutorials with instant feedback
   - Progressive difficulty levels from beginner to advanced
   - Achievement system and progress tracking
   - Community features and peer learning

**For Educators**
   - Course creation and management tools
   - Student progress monitoring
   - Custom exercise and assessment creation
   - Analytics and reporting dashboard

**For Developers**
   - CLI tools for automation and scripting
   - REST API for custom integrations
   - Extensible plugin architecture
   - Docker support for easy deployment

Platform Architecture
---------------------

Python Mastery Hub is built with modern technologies:

- **Backend**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: React with TypeScript
- **Authentication**: JWT with OAuth2 providers
- **Deployment**: Docker with Kubernetes support

.. mermaid::

   graph TB
       A[Web Browser] --> B[React Frontend]
       B --> C[FastAPI Backend]
       C --> D[PostgreSQL Database]
       C --> E[Redis Cache]
       C --> F[File Storage]
       
       G[CLI Tool] --> C
       H[Mobile App] --> C
       
       subgraph "External Services"
           I[GitHub OAuth]
           J[Google OAuth]
           K[Email Service]
       end
       
       C --> I
       C --> J
       C --> K

Documentation Structure
-----------------------

This documentation is organized into several sections:

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/core
   api/web
   api/cli

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/index
   tutorials/getting_started
   tutorials/basic_usage
   tutorials/advanced_features
   tutorials/deployment

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index
   examples/cli_examples
   examples/web_examples
   examples/api_examples

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/index
   development/architecture
   development/testing
   development/deployment

.. toctree::
   :maxdepth: 1
   :caption: Learning Content

   notebooks/01_python_basics
   notebooks/02_data_structures
   notebooks/03_oop_concepts
   notebooks/04_advanced_python
   notebooks/05_async_programming
   notebooks/06_web_development
   notebooks/07_data_science
   notebooks/08_testing_strategies

Community and Support
---------------------

Join our community and get help:

- 📖 **Documentation**: You're reading it!
- 🐛 **Bug Reports**: `GitHub Issues <https://github.com/python-mastery-hub/python-mastery-hub/issues>`_
- 💬 **Discussions**: `GitHub Discussions <https://github.com/python-mastery-hub/python-mastery-hub/discussions>`_
- 📧 **Email Support**: support@pythonmasteryhub.com
- 🐦 **Twitter**: `@PythonMasteryHub <https://twitter.com/PythonMasteryHub>`_

Contributing
------------

We welcome contributions from the community! Here's how you can help:

1. **Report Bugs**: Found a bug? `Open an issue <https://github.com/python-mastery-hub/python-mastery-hub/issues/new>`_
2. **Suggest Features**: Have an idea? Start a `discussion <https://github.com/python-mastery-hub/python-mastery-hub/discussions>`_
3. **Submit Code**: Check our `contributing guide <https://github.com/python-mastery-hub/python-mastery-hub/blob/main/CONTRIBUTING.md>`_
4. **Improve Docs**: Documentation improvements are always welcome
5. **Create Content**: Help us create learning materials and tutorials

License
-------

Python Mastery Hub is released under the MIT License. See the 
`LICENSE <https://github.com/python-mastery-hub/python-mastery-hub/blob/main/LICENSE>`_ 
file for details.

Changelog
---------

See our `CHANGELOG <https://github.com/python-mastery-hub/python-mastery-hub/blob/main/CHANGELOG.md>`_ 
for detailed release notes and version history.

Acknowledgments
---------------

Special thanks to:

- The Python community for creating an amazing ecosystem
- All contributors who have helped improve this platform
- Educational institutions using Python Mastery Hub
- Open source projects that made this possible

.. note::
   **Getting Started**: New to Python Mastery Hub? Start with our :doc:`tutorials/getting_started` guide.
   
   **Need Help**: Having trouble? Check our :doc:`tutorials/basic_usage` or reach out for support.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`