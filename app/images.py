# from dotenv import load_dotenv
# from imagekitio import ImageKit
# import os

# load_dotenv()

# imagekit = ImageKit(
#     private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
#     public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
#     url_endpoint=os.getenv("IMAGEKIT_URL")
# )

# IMAGEKIT_PRIVATE_KEY=private_MLvZmXqAqKx3uEOQiFRSVLFKlWg=
# IMAGEKIT_PUBLIC_KEY=public_CdQ0KxfIQjeH9e3NLllp+FXOa7o=
# IMAGEKIT_URL=https://ik.imagekit.io/nvvjn3ndu
from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY")
)