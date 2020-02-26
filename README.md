# crystalball-demo

This demo assumes the ConfigMap in question has been crafted with literal key/value pairs:

`kubectl create configmap app-config --from-literal=hello=world --from-literal=foo=bar`

Updates to the ConfigMap in S3 will then be detected by the crystalball cronjob and updated
on the master node.
