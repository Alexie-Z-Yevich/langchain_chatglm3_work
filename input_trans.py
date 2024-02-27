import os
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from ChatGLM3 import ChatGLM3
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAI

# input 后期换成用户输入
input_orin = "查询目标"
input_content = "查询附近的海玛斯"
# input_content = "查询半小时内发现的目标"
os.environ["OPENAI_API_BASE"] = 'https://oneapi.xty.app/v1'
os.environ["OPENAI_API_KEY"] = 'sk-DolLcIaoEKZbCyMN61A4362e988f4f3f93B6D8C5B4B85bDf'

llm = ChatGLM3()
# llm = OpenAI(max_tokens=3000)
prompt_template = ChatPromptTemplate.from_template(f"""
    要求来源接口："input_orin",
    要求查询内容："input_content",
    根据要求来源接口和要求查询数据，10字以内回答查询内容中的目标类型，如果没有目标类型回答无；
    用数字回答查询内容中的危险等级，如果没有危险等级回答1；
    用search_position()回答范围中心点经度和范围中心点维度，如果没有位置要求，返回search_position()否则返回search_position(x, y)；
    用数字回答范围半价，如果没有明确给出范围需求，回答无，如果有“附近、方圆”等词语且没有范围需求，回答默认2（公里），否则按照查询内容中的范围进行回答；
    按照查询内容回答发现目标起始时间，如果无需查询发现目标，回答无，否则按照当前时间12:00，对时间进行推理后回答，回答格式为11:30-12:00；
    可以参考的目标类型有：海玛斯：HIMARS、毒刺：MANPANDS、指挥营：CAMP、弹药库：DEPOT、雷达车：RADAR_TRUCK、指挥车：COMMAND_TRUCK
    可以参考的危险等级有：无危险：1、低危：2、中危：3、高危：4
    只需要按照引号中的格式回复，不要有多余内容。“目标类型：Answer Here 危险等级：Answer Here 范围中心点经纬度：Answer Here 范围半径：Answer Here 发现目标起始时间：Answer Here”
""")
# prompt_template = ChatPromptTemplate.from_template(f"""
#     按照如下格式找出要求查询内容的参数。参数格式如下：
#     “目标类型=；危险等级=；范围中心点经度=；范围中心点纬度=；范围半径=；发现目标起始时间=；发现目标截止时间=；"只需要输出上面引号内内容以及按要求补齐等号后面内容即可，不需要其他额外输出。
#     其中，目标类型的默认值为无、危险等级默认值为2、范围中心点经度的默认值为无、
#     范围中心点纬度的默认值为无、范围半径的默认值为2公里、发现目标起始时间的默认值为无、发现目标截止时间的默认值为无。
#     可以参考示例：
#     示例来源接口:"查询目标"
#     示例查询内容："查询（当前位置）（附近/方圆）5公里（内）的高危目标（高危目标对应危险等级为4）"
#     示例输出结果："目标类型=无；危险等级=4；范围中心点经度=调用查询函数(暂不调用)；范围中心点纬度=调用查询函数(暂不调用)；范围半径=5公里；发现目标起始时间=无；发现目标截止时间=无"
#     下面是正式的查询内容:
#     要求来源接口："input_orin",
#     要求查询内容："input_content",
#     要求输出结果：
# """)
# prompt_template = ChatPromptTemplate.from_template(f"""
#     按照如下格式找出要求查询内容的参数。参数格式如下：
#     “目标类型=；危险等级=；范围中心点经度=；范围中心点纬度=；范围半径=；发现目标起始时间=；发现目标截止时间=；"
#     其中，目标类型的默认值为无、范围中心点经度的默认值为无、
#     范围中心点纬度的默认值为无、范围半径的默认值为2公里、发现目标起始时间的默认值为无、发现目标截止时间的默认值为无。
#     可以参考示例：
#     示例来源接口:"查询目标"
#     示例查询内容："查询（当前位置）（附近/方圆）5公里（内）的高危目标"
#     示例输出结果："目标类型=无；危险等级=4；范围中心点经度=调用函数(暂不要求给出)；范围中心点纬度=调用函数(暂不要求给出)；范围半径=5公里；发现目标起始时间=无；发现目标截止时间=无"
#     要求来源接口："{input_orin}",
#     要求查询内容："{input_content}",
#     要求输出结果：
# """)
output_parser = StrOutputParser()
chain = (
    {"input_orin": RunnablePassthrough(), "input_content": RunnablePassthrough()}
    | prompt_template
    | llm
    | output_parser
)
input_orin = {"input_orin": input_orin}
input_content = {"input_content": input_content}
result = chain.invoke(input_orin, input_content)
print(result)




# chinese_prompt = PromptTemplate(template=prompt_template, input_variables=["input_orin", "input_content"])
#
# chain = load_summarize_chain(llm, prompt=chinese_prompt)
#
# # docs = url2News(url)
#
# out_put = chain.invoke(input_orin, input_content)
# # out_put = chat_model.invoke("找出下面这段话中的参数：“查询（当前位置）（附近/方圆）5公里（内）的高危目标”，"
# #                   "并且以“目标类型={目标类型}；危险等级={}；范围中心点经度={}；范围中心点纬度={}；范围半径={}；发现目标起始时间={}；发现目标截止时间={}；”的格式输出，"
# #                   "如果没有这个参数，请给一个默认参数替代")
# print(out_put)