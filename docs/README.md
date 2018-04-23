Sources for the `comply` site, found at [http://jhauberg.github.io/comply](http://jhauberg.github.io/comply)

## Building

Run the `build.py` script to assemble the site pages.

```
$ python build.py
```

*Note that output is overwritten without warning*

### Assembling

The script takes the base template ([base/index.html](base/index.html)) and inserts all rule components ([base/rules/\*](base/rules/)) into the appropriate sections, finally outputting an assembled [index.html](index.html).

No particular processing is done; it's all pretty simple. Each rule component is expected to fit as-is when inserted into the template.
