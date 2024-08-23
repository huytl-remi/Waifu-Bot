def get_cached_content():
    try:
        with open('./memory/cached_content.txt', 'r') as file:
            return file.read()
    except FileNotFoundError:
        print("Warning: cached_content.txt not found. Using default content.")
        return """
        This is default additional information for the bot to know:
        1. Be respectful to all members
        2. No spamming or excessive self-promotion
        3. Use appropriate language
        4. Stay on topic in dedicated channels
        """
