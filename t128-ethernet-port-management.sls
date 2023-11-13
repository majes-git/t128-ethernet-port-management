{% set sbin_path = "/usr/local/sbin" %}
{% set pyz = "t128-ethernet-port-management.pyz" %}
{% set wrapper = "t128-ethernet-port-management.sh" %}
{% set config_file = "/etc/128technology/t128-ethernet-port-management.yaml" %}

t128-ethernet-port-management config:
  file.managed:
    - name: {{ config_file }}
    - mode: 644
    - contents: |
        debug: false
        ports:
          - '0000:00:14.0': corp
          - '0000:00:15.0': corp
          - '0000:00:16.0': guest
          - '0000:00:17.0': iot
          - '0000:01:01.0':
              -  10: corp
              -  20: guest
              - 128: iot

t128-ethernet-port-management script:
  file.managed:
    - name: {{ sbin_path }}/{{ pyz }}
    - mode: 755
    - source: salt://{{ pyz }}

t128-ethernet-port-management wrapper:
  file.managed:
    - name: {{ sbin_path }}/{{ wrapper }}
    - mode: 755
    - contents: |
        #!/bin/sh
        exec {{ sbin_path }}/{{ pyz }} "$0" "$@"

t128-ethernet-port-management create symlinks:
  cmd.run:
    - name: {{ sbin_path }}/{{ wrapper }} --create-symlinks
    - onchanges:
      - file: {{ config_file }}
