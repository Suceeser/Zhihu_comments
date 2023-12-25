import requests
import execjs


class zhihuSpider():
    def __init__(self):
        self.ctx = execjs.compile(open('x96.js', 'r', encoding='utf-8').read())
        self.cookies = {
            '_zap': '6eb98055-ad68-4e2a-86f0-a07c9b7565d1',
            'd_c0': '',
            'YD00517437729195%3AWM_TID': 'ZTBJf%2BHI1wxFRERQEBLEzIoYAeVoXXU6',
            '__snaker__id': 'evZ7WGWiWeejVMBh',
            '_xsrf': '8bd409b0-aee2-4e29-9d53-901838e2a34c',
            'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49': '1697695113,1697721231,1697738052,1697808664',
            'gdxidpyhxdE': '4SL3hY3M62d4Hwhs%5CwQmOLdw4j1diCaz2U4BN6rlIk%2FiOPByQD3je%5CSyBh%2FAaNm%5CH3g5szt63DXLGGEylf10S2uRQpvsf3rNA6vz%5CyKBuMGekOetpr9PttJ%2B0utBo8XIa1RDgO3KQztkqdHkeCM8lgGsjLdx73lmRA2k7%2BAC3bOiBVaV%3A1697809573312',
            'YD00517437729195%3AWM_NI': 'fc8EYiaP39YPLe65gMb2OqY0bQOAx5d%2B3IO%2FszttcjNubkdYoEiVmI38Q7MXKBbH0OvXBjw5PCWqn6xgAHb%2BTqkbGMYs58BdkwNuyjNDlpAERiIP1JTjsIZ5JUzbJdv9Mkg%3D',
            'YD00517437729195%3AWM_NIKE': '9ca17ae2e6ffcda170e2e6eeb2e221b1bd008bce44e9e78fb7c14b929a8bacd872f188fdaecd5ffbe9afd0ea2af0fea7c3b92aa6bdf8a6dc63a390fddadc5c90bbfad6e647a2ee8192dc3ca28f81a2fb3fa8f5fdaace25b1a6bc95e2628eabae8ce753ad9ba7b7f043f1e89fd8d054899eaea9b345b6888e8bf63f949d9992ed3ebcb98fa9e12198afa583c6479badfbd9c170a9a98296fc628e9ca491c44f92b787b1b44298b6bdaad93f8a8bb683c970b6e7838ce637e2a3',
            'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49': '1697808746',
            'captcha_session_v2': '2|1:0|10:1697808748|18:captcha_session_v2|88:TmxOemVaU2MvaFFnRW1wWGt0ejJMblRKZm9aQWl1MitTQVkyb20xcTEyeGFydzFicEQ0M0gvZUF2dXh1TGtUSQ==|12fbfe3713e0f10d78ded2e5634a49a916b4e7f9a215938c83e11f27e289390b',
            'KLBRSID': 'fb3eda1aa35a9ed9f88f346a7a3ebe83|1697808781|1697808663',
        }
        self.headers = {
            'authority': 'www.zhihu.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.zhihu.com/question/289222749/answer/2251138943',
            'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'x-requested-with': 'fetch',
            'x-zse-93': '101_3_3.0',
        }

        self.comment_num = 0
        self.comments = []

    def fetch(self, url_info):
        self.headers['x-zse-96'] = '2.0_' + self.ctx.call('get_x96', f"101_3_3.0+{url_info}+{self.cookies['d_c0']}")
        for try_times in range(4):
            try:
                response = requests.get(
                    f'https://www.zhihu.com' + url_info,
                    cookies=self.cookies,
                    headers=self.headers,
                )
                return response
            except Exception as e:
                print(f'评论获取失败，报错url为{"https://www.zhihu.com" + url_info}\n错误信息为{e}\n剩余尝试次数{3 - try_times}')

    def fetch_root_comment(self, comment_url):
        '''
        获取所有根评论，并调用解析函数
        '''
        response = self.fetch(comment_url)
        json_data = response.json()
        if len(json_data["data"]) == 0:
            print(f"文章id{comment_url.split('answers/', 1)[1].split('/', 1)[0]}评论后续已抓取完毕")
            print(f'评论共{self.comment_num}个\n', self.comments)
            '''
            在这里加评论处理逻辑
            '''
            return
        self.parse_comment(json_data["data"], init=True)
        print('即将获取根评论链接:\n', json_data["paging"]["next"])
        # 尝试获取后面的根评论
        self.fetch_root_comment(json_data["paging"]["next"].replace('https://www.zhihu.com', ''))

    def fetch_child_comment(self, comment_info, new_url=False):
        '''
        获取所有二级评论内容
        '''
        comment_info = f'/api/v4/comment_v5/comment/{comment_info}/child_comment?order_by=ts&limit=20&offset=' if not new_url else comment_info.replace(
            'https://www.zhihu.com', '')
        response = self.fetch(comment_info)

        json_data = response.json()
        if len(json_data["data"]) == 0:
            print('该评论后续已抓取完毕')
            return
        return self.parse_comment(json_data["data"]), json_data["paging"]["next"]

    def parse_comment(self, comment_data, init=False):
        '''
        解析评论，如果有二级评论，则加入到一级评论后面
        如果二级评论没有获取全，则再次请求后面的耳机评论内容
        '''
        # 简单解析，需要解析更多内容请见评论接口返回的内容
        simple_data = [
            {
                "comment_id": item.get("id"),
                "is_top": item.get("is_author_top"),
                "content": item.get("content"),
                "created_time": item.get("created_time"),
                "is_delete": item.get("is_delete"),
                "reply_comment_id": item.get("reply_comment_id"),
                "reply_root_comment_id": item.get("reply_root_comment_id"),
                "like_count": item.get("like_count"),
                "dislike_count": item.get("dislike_count"),
                "is_author": item.get("is_author"),
                "user_url_token": item["author"].get("url_token"),
                "user_name": item["author"].get("name"),
                "is_anonymous": item["author"].get("is_anonymous"),
                "vip_info": item["author"].get("vip_info").get("is_vip"),
                "ip_info": item.get("comment_tag"),
                "personal_introduction": item["author"].get("headline"),
                "child_comment_count": item.get("child_comment_count"),
                "child_comments": item.get("child_comments"),
            }
            for item in comment_data]
        for item in simple_data:
            simple_child_comment = []
            if item["child_comment_count"] and item["child_comment_count"] == len(item["child_comments"]):
                simple_child_comment = self.parse_comment(item["child_comments"])
            if item["child_comments"] and item["child_comment_count"] > len(item["child_comments"]):
                simple_child_comment, next_url = self.fetch_child_comment(item["comment_id"])
                if item["child_comment_count"] != len(simple_child_comment):
                    while len(simple_child_comment) != item["child_comment_count"]:
                        other_simple_child_comment, next_url = self.fetch_child_comment(next_url, True)
                        simple_child_comment += other_simple_child_comment
            if simple_child_comment:
                item["child_comment_count"] = 0
                item["child_comments"] = []
            if init:
                self.comment_num += len([item] + simple_child_comment)
                self.comments.append([item] + simple_child_comment)
        return simple_data

def fetch_comments(target_answer_ids):
    print('如果失效，请更新cookie，主要是d_c0参数')
    for target_answer_id in target_answer_ids:
        zhihuSpider().fetch_root_comment(
            f'/api/v4/comment_v5/answers/{target_answer_id}/root_comment?order_by=score&limit=20&offset=')


if __name__ == '__main__':
    target_answer_ids = [
        3114298172, 1244535507
    ]
    fetch_comments(target_answer_ids)
