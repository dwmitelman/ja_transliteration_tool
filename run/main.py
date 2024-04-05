from run.e2e_pipe import Import, PipelineManager

initial_input = Import()

output_format = "by_list_str"
# output_format = "by_docx_path"

initial_input.by_docx_path("https://docs.google.com/document/d/1UvOKooSgNCr2jkcbmSDo_v_gGyqQ7d9Z4A-Whd1c9kc/edit?usp=sharing")
# initial_input.by_list_str(text)

pm = PipelineManager(initial_input.output(), output_format=output_format)

if output_format == "by_list_str":
    print("Your transliteration is ready! Here are the results:")
    for sentence in pm.output():
        print("JA input: ")
        print(sentence[0])
        print("Transliterated output: ")
        print(sentence[1])
        print()

elif output_format == "by_docx_path":
    print(f"Your transliteration is ready! Please visit: {pm.output()}")
