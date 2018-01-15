# comply

What constitutes well-written C?

I think we can all agree that opinions on this are numerous. You probably have one too.

Compilers do not usually care how you write your code. They're happy as long as it does not contain errors. Humans, however, do (or at least, _should_) care.

This project defines and applies some (very) opinionated and strict rules on best practices for writing readable and maintainable C. Following these rules will help enforce consistency throughout your project. You might not like some of them, but each has thought and reasoning behind it.

Basically, `comply` is a style linter that scans and analyzes your code, looking for things that could be improved. It is _not_ a compiler- as such, it will not find errors in your code. It only provides suggestions on improvements; it never touches or changes your code.

You decide which rules are worth following. Just remember, consistency is key.

Many of the rules, if not most, are based on [Malcolm Inglis' style guidelines](https://github.com/mcinglis/c-style).

# Installation

Install straight from the source:

```console
$ python setup.py install
```

<details>
  <summary><strong>It doesn't work</strong></summary>

There's a few things that could go wrong during an install. If things didn't go as expected, check the following:

**You may have more than one Python version installed**

Some systems may have multiple Python versions installed and available. This project requires Python 3.5 or later, so you may need to specify that you want to use a later version:

```console
$ python3 setup.py install
```

**Your PATH environment variable may be incorrect**

When you first installed Python, the installer probably added the `PATH` automatically to your `~/.profile` or `~/.bash_profile`. However, in case it didn't, it should look something like this:

```bash
PATH="/Library/Frameworks/Python.framework/Versions/3.6/bin:${PATH}"
export PATH
```

You may additionally need to add the `PYTHONPATH` variable and have it point to the `site-packages` directory of your Python version; for example, for a Python 3.6 installation, the variable could look like this:

```bash
export PYTHONPATH="${PYTHONPATH}/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages"
```

</details>

<details>
  <summary><strong>Uninstalling</strong></summary>

If you want to uninstall `comply` and make sure that you get rid of everything, you can run the installation again using the additional **--record** argument to save a list of all installed files:

```console
$ python setup.py install --record installed_files.txt
```

You can then go through all listed files and manually delete each one.

</details>

# Usage

When installed, you can run `comply` on the command line:

```console
$ comply src/
```

<details>
  <summary><strong>Running without installing</strong></summary>

You can also run `comply` without installing it. However, in that case, you must execute the `comply` module as a script.

Assuming working directory is the root of the project, you go like this:

```console
$ python -m comply path/to/src/
```

</details>

## Requirements

This project strives to keep dependencies at an absolute minimum.

  * Python 3.5+
  * [docopt](https://github.com/docopt/docopt) - provides a nicer command-line interface

## Full usage

```console
Make your C follow the rules

Usage:
  comply <input>...
  comply -h | --help

  comply --version

Options:
  -h --help    Show program help
  --version    Show program version
```

## License

See [LICENSE](LICENSE)