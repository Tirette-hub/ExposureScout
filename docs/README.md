# Welcome to **_Exposure Scout_** Documentation
As stated in the main page of the project, _Exposure Scout_ in two modules:
- [core](./CORE.md)
- [modules](./MODULES.md)

## Using exposurescout package
If you want to use this project as a package/API, you can do so by simply importing _exposurescout_ itself.
```python3
import exposurescout as es
```
It already imports all the data, methods, functions, classes and objects from _core_ and _modules_ so you do not need to do it manually.

## Developping new Collector
To develop new collector, you will need to create a new collector object that inherits from [ACollector](./COLLECTOR.md#acollector). All the methods you **MUST** implement are listed in the documentation (Feel free to have a look to [LinUsersCollector documentation](./COLLECTOR.md#linuserscollecor) and/or [implementation](../exposurescout/modules/LinUsersCollector.py)).

If your collector relies on any script (such as bash), place them in the [scripts](../scripts) directory to keep the project as clean as possible.

When your collector is ready, **do not forget to set a unique type as bytes** (_snapshot_elemnt_id_).

You also need to implement a *simple* data structure for your collectibles that your collector will collect. It **MUST** then inherit from [ACollectible](./COLLECTOR.md#acollectible).

*Note: [ACollector](./COLLECTOR.md#acollector) and [ACollectible](./COLLECTOR.md#acollectible) act like a mix between interfaces and abstract classes in Java.*