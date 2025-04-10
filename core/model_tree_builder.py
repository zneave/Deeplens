def build_tree_from_layers(layers):
    tree = {}

    for layer in layers:
        path = layer["name"].split(".")
        current = tree
        for part in path[:-1]:
            current = current.setdefault(part, {})
        current[path[-1]] = layer  # leaf

    return tree
