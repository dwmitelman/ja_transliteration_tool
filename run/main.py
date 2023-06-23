from friedberg.run.e2e_pipe import Import, PipelineManager

initial_input = Import()
# initial_input.by_list_str(text)
initial_input.by_docx_path("https://docs.google.com/document/d/1UvOKooSgNCr2jkcbmSDo_v_gGyqQ7d9Z4A-Whd1c9kc/edit?usp=sharing")
pm = PipelineManager(initial_input.output())
print(f"Your transliteration is ready! Please visit: {pm.output()}")
