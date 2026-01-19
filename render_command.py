import subprocess


def build_kicad_cli_command(options):
    args = [
        "kicad-cli",
        "pcb",
        "render",
        "--output",
        options["output"],
        "--width",
        str(options["width"]),
        "--height",
        str(options["height"]),
        "--side",
        options["side"],
        "--background",
        options["background"],
        "--quality",
        options["quality"],
    ]
    preset = options.get("preset", "")
    if preset:
        args.extend(["--preset", preset])
    if options.get("floor"):
        args.append("--floor")
    if options.get("perspective"):
        args.append("--perspective")
    zoom = options.get("zoom", "")
    if zoom:
        args.extend(["--zoom", zoom])
    pan = options.get("pan", "")
    if pan:
        args.extend(["--pan", pan])
    pivot = options.get("pivot", "")
    if pivot:
        args.extend(["--pivot", pivot])
    rotate = options.get("rotate", "")
    if rotate:
        args.extend(["--rotate", rotate])
    light_top = options.get("light_top", "")
    if light_top:
        args.extend(["--light-top", light_top])
    light_bottom = options.get("light_bottom", "")
    if light_bottom:
        args.extend(["--light-bottom", light_bottom])
    light_side = options.get("light_side", "")
    if light_side:
        args.extend(["--light-side", light_side])
    light_camera = options.get("light_camera", "")
    if light_camera:
        args.extend(["--light-camera", light_camera])
    light_side_elevation = options.get("light_side_elevation", "")
    if light_side_elevation:
        args.extend(["--light-side-elevation", light_side_elevation])
    args.append(options["board"])
    return subprocess.list2cmdline(args)


def build_cmd_exe_command(kicad_cmd_path, kicad_cli_cmd):
    return f'cmd.exe /c ""{kicad_cmd_path}" && {kicad_cli_cmd}"'
