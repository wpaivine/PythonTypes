## Static Interprocedural Analysis for Automatic Python Type Annotation
Python type hinting is cool. Old code which you need to convert to use hinting is not cool. It
would be nice to automatically add hinting to old code, so you don't have to waste your time. With
interprocedural analysis, this is (partly) possible!.

Note that as this is a static analysis, it won't be 100% accurate or precise. But the assumptions
that it makes should be correct. Additionally, this project still has a lot of work to do as far as
the type system (no parametric function types), so don't expect much on that front. Likewise, due
to other python-dynamic reasons, class methods are currently completely ignored.

### Running
If you still want to try and use this, it should be fairly straightforward. Clone this directory,
and run

`python run.py -a output.py input.py`

Note that you need python3(.6?) for this to work. 
