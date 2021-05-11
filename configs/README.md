# Raspimon Alert Tuning

This section describes how you can write and tune your alarm configuration `.yaml`. Tuning the alarm configuration helps to trigger alerts when the condition is met. Multiple breaches are raised and summarized into a single alert.

Here is how a simple alert configuration looks like:
```yaml
host:
  cpu:
    name: "CPU Utilization Alarm"
    thresholds:
      -
        consecutive: 2
        description: "CPU Utilization has gone above threshold limit"
        interval: 300
        threshold: 70
        trend: "geq"
  
  mem:
    name: "Memory Utilization alarm"
    thresholds:
      -
        description: "Memory Utilization has gone above threshold limit"
        threshold: 70
        trend: "geq"

processes:
  omv:
    name: "OpenMediaVault NAS service alarm"
    process: "omv-engined"
    thresholds:
      -
        consecutive: 2
        description: "OpenMediaVault NAS service is down"
        interval: 150
        state: "down"
  nginx:
    name: "NGINX process alarm"
    process: "nginx"
    thresholds:
      -
        description: "NGINX service is down"
        state: "down"

```

## Alert Sections
Alerts are divided into various sections depending on the nature of the resource eg. `host`, `processes`. Resources like `mem` and `cpu` are host level metrics, where as `nginx` process is a `processes` level metric.

### Host Alerts
Host alerts are alerts are [supported](../modules/utils/Stats.py#L35) by the current code state. Each alert should mandatorily specify its `name` and the `thresholds` list block. Each threshold in the thresholds block is checked for a breach. A threshold block can be configured in two modes - consecutive & live. Take a look at the [modes](#modes) section for more details.

You can set multiple thresholds per dimension for a mix-and-match result. As can be seen above, the CPU alarm will go off if the utilization breaches the `70%` mark (greater-than-or-equal-to `geq`) consecutively `2` times within a span of `300` seconds. Whereas the Memory alarm will go off if the last read was `geq` than `70%`.

Bear in mind that certain fields like `name`, `description`, legal `trend` values, `thresholds` need to be stated mandatorily. This is to ensure that the config remains sound enough without having to scan through the code. Missing any of them will result in immediate abort. Adding a host metric that is not supported could result in validation error on program start up or can get ignored.

### Process Alerts
Process alerts can be configured to look for a process name and based on its state. In the above example, the NGINX alarm will go if the last ready found that the process `nginx` is `down`, whereas the OpenMediaVault will go off if the `ovm-engined` process has been `down` consecutively for the 2 most recent reads in last 150 seconds. Similarly you can configure another process `my-process` and configure it as `up` if it is supposed to be down. During a check situation if the your process is found to be running, it will be flagged and an alert will be generated.

Process names are supposed to be exact, however the implementation allows for a substring match for some flexibility by giving up some corner cases.

## Modes
Following are the modes supported for a threshold block:
- `consecutive`: A threshold block is supposed to be a consecutive mode when it contains the keyword `consecutive` whose numeric value is > 1. It also requires the block to then specify an `interval` (in seconds) - failing to do so will lead to an initial validation error and abort. To meet a breach, all reads values in last `interval` seconds must meet the specified `trend`/`status` as well as meet the `consecutive` minimums. 

    This means that if the current number of reads is insufficient, the alarm wont go off. Similarly if the number of reads is sufficient but one of the _N_ consecutive data fails to breach, the alarm wont go off.

- live (absence of `consecutive`): When a `consecutive` block is not specified the breach check is assumed to by only applied to the most recent read metric. There is no role of `interval` and hence is not required. If no reads are present, the alarms are considered OK.


_< [Go back main documentation](../README.md)_

<hr>

> (c) _jaiwardhan/raspimon_