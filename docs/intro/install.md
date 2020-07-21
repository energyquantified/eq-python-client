# Installation

**Requirements:** The Energy Quantified Python client is developed for
**Python 3.7 or newer**.

## Install

To install with **pip** type:

```bash
# Install package
pip install energyquantified

# Upgrade package
pip install --upgrade energyquantified
```

Or you could use **conda**:

```bash
# Install package
conda install energyquantified

# Update package
conda update energyquantified
```

The `energyquantified` package does not automatically pull in `pandas` or
any other data analysis libraries, because they are **not** required to use
this package.

If you would like to use `pandas`, `matplotlib`, `seaborn` or other
similar libraries you must install them separately:

```bash
pip install pandas matplotlib seaborn
```

## Verify installation

Start the Python interactive shell and import `energyquantified`:

    >>> import energyquantified

If the above import was successful, you are good to go.

## Get the source code

The project is hosted on GitHub. If you find any bugs, please report them
on GitHub. Pull requests are welcome!

[https://github.com/energyquantified/eq-python-client](https://github.com/energyquantified/eq-python-client)