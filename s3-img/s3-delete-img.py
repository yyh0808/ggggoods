import boto3
from botocore.exceptions import NoCredentialsError

# R2 配置
R2_ENDPOINT = 'https://06898acc14d0b9633f259fe20145fd49.r2.cloudflarestorage.com'
R2_ACCESS_KEY_ID = 'a8b4070c0d1721c6dfba49be0844220f'
R2_SECRET_ACCESS_KEY = 'd8498c36c3fd3fd8f36665d874e15bcb12efc101a38468a88d40d8e4948e5077'
R2_BUCKET_NAME = 'ggggoods-blog'

# 要删除的文件所在的目录（不包括 /2024）
PREFIX_TO_DELETE = ''  # 如果文件在根目录，就保持为空字符串

# 指定要删除的文件类型
FILE_EXTENSIONS_TO_DELETE = ('.png', '.jpg', '.jpeg')

def delete_files():
    """删除指定前缀和文件类型的所有文件"""
    s3_client = boto3.client('s3',
                             endpoint_url=R2_ENDPOINT,
                             aws_access_key_id=R2_ACCESS_KEY_ID,
                             aws_secret_access_key=R2_SECRET_ACCESS_KEY)

    try:
        # 列出所有符合条件的对象
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=R2_BUCKET_NAME, Prefix=PREFIX_TO_DELETE)

        delete_list = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    if (not key.startswith('2024/') and 
                        any(key.lower().endswith(ext) for ext in FILE_EXTENSIONS_TO_DELETE)):
                        delete_list.append({'Key': key})

        if not delete_list:
            print("没有找到需要删除的文件。")
            return

        # 批量删除文件
        while delete_list:
            # S3 API 限制每次最多删除 1000 个对象
            batch = delete_list[:1000]
            response = s3_client.delete_objects(
                Bucket=R2_BUCKET_NAME,
                Delete={'Objects': batch}
            )
            delete_list = delete_list[1000:]

            # 打印删除结果
            if 'Deleted' in response:
                print(f"成功删除了 {len(response['Deleted'])} 个文件。")
            if 'Errors' in response:
                print(f"删除过程中出现 {len(response['Errors'])} 个错误。")
                for error in response['Errors']:
                    print(f"错误: {error['Key']} - {error['Code']}")

    except NoCredentialsError:
        print("凭证无效 - 请检查您的访问密钥和秘密密钥")
    except Exception as e:
        print(f"删除文件时发生错误: {str(e)}")

if __name__ == "__main__":
    print(f"警告：此操作将删除指定目录下的所有 {', '.join(FILE_EXTENSIONS_TO_DELETE)} 文件（不包括 /2024 目录）。")
    confirmation = input("确定要继续吗？(y/n): ")
    if confirmation.lower() == 'y':
        delete_files()
    else:
        print("操作已取消。")