def normal_text():
    print("Start function")
    text = ""
    
    for i in range(3):
        print(f"Generating part {i}")
        text += f"Chunk-{i}\n"
    
    print("Returning full text")
    return text


result = normal_text()
print("Received result:")
print(result)
