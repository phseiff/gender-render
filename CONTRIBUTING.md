# Contribution Guidelines

Contributions in the form of issues and pull-requests as well as suggestions as questions are always welcome.
However, please consider the following.

## In regards to the specification

The specification (make sure you are acquainted at least with the core specification before engaging in its developement) as well as its extension specifications follow semantic versioning as outlined by the core specification;
bugfix-releases correspond to to releases with merely changes in wording.
If you want to make a change in the wording of a specification, to make it more clear, fix spelling mistakes or grammatical errors, or simply fix smaller wording issues (I am not a native english speaker), you can issue a pull request or raise an issue in which you offer to make a pull request or ask to fix them;
for all other changes (major as well as inor releases), you should raise an issue to discuss the proposed change before trying to make a pull request.

In regards of the file structure, note that the files in `docs/specs/*` may not be changed in a pull request, since they are managed by a script.
The right place for changes are the `.tex` files directly in `docs`.
Also, note that a files version (in the `doc` folder) is not increased when developement of a new version begins, but rather when it finishes, since increasing the number automatically triggers a script that uploads the new specification version to the download page.

Please be aware that there may already be changes planned at the time of you proposing them, so even if your proposed changes are good and necessary, there is no guarantee that your implementation concept will be the one chosen at the end.
Please be aware, additionally, that maintainers already having detailed plans on how to implement a feature can be a reason for not choosing your suggested approach to a problem even if your approach is a good one, for example due to discrepancies in the preferred way of going about this.

## In regards to the implementation

There are several comments marked as ToDo in the specification.
These comments all indicate something that is considered a feature worth implementing, so if you want, go for it and implement it, then make a pull request.
The feature is generally accepted.
However, in some of these cases, it might be ambiguous where to add them, e.g. which function, pipeline or class.
In general, if the changes you want to add cause existing tests to fail by changing the way a certain function behave, or add functionality to a function that one wouldn't assume it to have based on its name and/or docstring, please raise an issue to discuss it before doing your pull request.
Raising an issue before implementing a change for a pull-request is also a good choice in general, and if you plan to add new classes/files and reformat existing code, you should assume raising an issue before starting with an implementation to definitely be a good idea.

The implementation follows PEP8 standards, with some exceptions like the dict describing the finite state machine in `parse_templates.py`, which would simply look messy if it was formatted according to PEP8.
The code also strives for 100% code coverage, and no dead code unless for a good reason (see `test/vulture_whitelist.py`), and follows semeantic versioning.
Every function, method and class needs to have a docstring and ideally, comments where necessary.

Please also note that the implementation **has** to follow the latest version of the specification, so adding features that do not comply with it or change the way the rendered behaves from how the spec defines it too is not supported.
See [above](#in-regards-to-the-specification) on how to contribute to the specification.

## In general

In general, any contribution (issue as well as pull request) is appreciated, but the chance of them bearing fruits and not being rejected drastically increases if you follow the aforementioned set of standards.
However, please be aware that not every contribution can be guaranteed to make it into the code/ the specification for many reasons, such as differences in vision and perspective;
I will, however, be committed to making sure that contributions don't get rejected at frustratingly or unnecessary late stages of their development to the fullest extend possible.

## Further reading

See also [our code of conduct](CODE_OF_CONDUCT.md).

Happy contributing!
