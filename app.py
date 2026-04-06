import gradio as gr

def run(x):
    return f"Processed: {x}"

iface = gr.Interface(fn=run, inputs="text", outputs="text")
iface.launch()