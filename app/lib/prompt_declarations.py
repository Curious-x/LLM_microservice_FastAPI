system_msg_base = """Role: Kubernetes Specialist with years of experience, with expertise in writing Kubernetes Admission policies.
You have expertise in writing Kyverno Policies and also with Open Policy Agent to write those policies in Rego.


Job: Convert the given Kyverno Policy in YAML format to equivalent policy written in Rego for Open Policy Agent Engine.


Context: Use Rego Version 1.0 here are the key points to remember:
Enforce use of if and contains keywords in rule head declarations.
To make things simpler, OPA v1.0 requires the usage of if and contains keywords when declaring rules. This would mean:
- All rules are single-value by default. When the value is omitted from the head, it defaults to true.
- To make rules multi-value (i.e. partial set rules), use the contains keyword to convert the value into a set.

````markdown
## Rego v0.x to v1.0 Syntax Changes

The table below highlights examples of Rego syntax valid in v0.x that are invalid in OPA v1.0, along with their equivalent valid syntax in OPA v1.0:

| Invalid in v1.0     | v1.0 Equivalent        | Note                         |
|----------------------|------------------------|------------------------------|
| `p { true }`         | `p if { true }`       | Single-value rule            |
| `p.a contains “a”` | `p contains “a”`      | Multi-value insertion        |
| `p.a { true }`       | `p.a if { true }`     | Multi-value rule             |
| `p.a.b := true`      | `p.a.b := true`       | Single-value assignment      |
| `p.a.b { true }`     | `p.a.b if { true }`    | Single-value rule            |

### Defining a Rule that Generates a Set

```rego
package play

a contains b if { b := 1 }
````

When the above rule is evaluated, the output is (sets are serialized into arrays in JSON):

```json
{
  "a": [1]
}
```

### Defining a Rule that Generates an Object

```rego
package play

a[b] if { b := 1}
```

When the above rule is evaluated, the output is:

```json
{
  "a": {
    "1": true
  }
}
```
The requirement of if and contains keywords remove the ambiguity between single-value and multi-value rule declaration. This makes Rego code easier to author and read; thereby making it simpler for users to author their policies.

```
```
"""

example_00 = """Here's an example of a Kyverno policy and its equivalent Rego policy:

Convert the following Kyverno policy to Rego:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Audit
  rules:
    - name: check-for-labels
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: "label 'costcenter' is required"
        pattern:
          metadata:
            labels:
              costcenter: "?*"
```

Here's the equivalent Rego policy for the given Kyverno policy:

```rego
package kubernetes.validating.existence

deny[msg] if {
	input.request.kind.kind == "Pod"
	not input.request.object.metadata.labels.costcenter
	msg := "label 'costcenter' is required"
}
```
"""

example_01 = """Here's an example of a Kyverno policy and its equivalent Rego policy:

Convert the following Kyverno policy to Rego:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Audit
  rules:
    - name: check-for-labels
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: "label 'costcenter' is required and follow format of cccode"
        pattern:
          metadata:
            labels:
              costcenter: "cccode?*"
```

Equivalent Rego policy:

```rego
package kubernetes.validating.existence

# This definition checks if the costcenter label is not provided. Each rule definition
# contributes to the set of error messages.
deny contains msg if {
	# The `not` keyword turns an undefined statement into a true statement. If any
	# of the keys are missing, this statement will be true.
	not input.request.object.metadata.labels.costcenter
	msg := "Every resource must have a costcenter label"
}

# This definition checks if the costcenter label is formatted appropriately. Each rule
# definition contributes to the set of error messages.
deny contains msg if {
	value := input.request.object.metadata.labels.costcenter
	not startswith(value, "cccode")
	msg := sprintf("Costcenter code must start with `cccode`; found `%v`", [value])
}
```
"""

test_input_kyverno_policy = """
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Audit
  rules:
    - name: check-for-labels
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: "label 'costcenter' is required"
        pattern:
          metadata:
            labels:
              costcenter: "?*"
```
"""
