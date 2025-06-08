import torch
from diffusers import StableDiffusionPipeline

# 初始化Stable Diffusion模型
model_id = "CompVis/stable-diffusion-v1-4"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")


def generate_image(prompt):
    """
    根据给定的文本提示生成图像。
    :param prompt: 文本提示
    :return: 生成的图像
    """
    image = pipe(prompt).images[0]
    return image


if __name__ == "__main__":
    test_prompt = "Protein plays a crucial role in muscle repair and growth, especially when paired with regular resistance or endurance training. After a workout, your muscles are primed to absorb nutrients, making it an ideal time to consume high-quality protein. Aim for 1.6–2.2 grams of protein per kilogram of body weight daily to support muscle maintenance and development. Sources like lean meats, eggs, dairy, and plant-based proteins provide essential amino acids for recovery. Spacing protein intake evenly throughout the day maximizes its benefits. Remember, while supplements like whey can be convenient, whole foods should be the foundation of your diet. Combine smart nutrition with consistent training for optimal results."
    generated_image = generate_image(test_prompt)
    generated_image.save("test_image.png")
    print("Image generated and saved as test_image.png") 