Set up the development environment
=======================================

To set up the development environment for cliasi, follow these steps:

**Clone the Repository**:
   First, clone the cliasi repository from GitHub to your local machine:

   .. code-block:: bash

       git clone https://github.com/IgnyteX-Labs/cliasi.git

**Install dev dependencies**:
   Navigate to the cloned repository and install the development dependencies using pip:

   .. code-block:: bash

       cd cliasi
       pip install -e .[dev]
       # Optional: install docs dependencies too
       pip install -e .[docs]

**Run Tests**:
    You can run the test suite using pytest to ensure everything is set up correctly:

    .. code-block:: bash

        pytest

**Build Documentation**:
    To build the documentation run the following sphinx command:

    .. code-block:: bash

        sphinx-build -b html docs/source docs/build/html