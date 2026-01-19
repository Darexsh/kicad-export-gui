def bind_mousewheel(root, canvas):
    def _on_mousewheel(event):
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

    canvas.bind("<Enter>", lambda _e: root.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda _e: root.unbind_all("<MouseWheel>"))
    canvas.bind(
        "<Enter>",
        lambda _e: root.bind_all("<Button-4>", _on_mousewheel),
        add="+",
    )
    canvas.bind(
        "<Enter>",
        lambda _e: root.bind_all("<Button-5>", _on_mousewheel),
        add="+",
    )
    canvas.bind(
        "<Leave>",
        lambda _e: root.unbind_all("<Button-4>"),
        add="+",
    )
    canvas.bind(
        "<Leave>",
        lambda _e: root.unbind_all("<Button-5>"),
        add="+",
    )
