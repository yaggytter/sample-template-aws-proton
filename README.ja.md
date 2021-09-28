# AWS Proton 用 サンプルテンプレート (EC2 ベース)

AWS Proton 用 サンプルテンプレート (EC2 ベース) です！ 公式のサンブル [AWS Proton sample templates](https://github.com/aws-samples/aws-proton-sample-templates) をベースに作っています。

## このテンプレートを使うとどんなものができるのか？

![diagram](./docs/diagram.png)

こんな感じです！

## どうやって使うのか？

いわゆるふつーの AWS Proton の使い方で使います。ただしマルチアカウント前提になっています。
また、いまのところ東京リージョン(ap-northeast-1)専用になっています。(AMI の都合で手抜きしてます)

手順

- AWS Proton 用に「管理アカウント」「環境アカウント」の２つの AWS アカウントを用意します

  - https://docs.aws.amazon.com/proton/latest/adminguide/ag-setting-up.html ここのやり方を参考にしてください。
  - アプリケーションコードのリポジトリは、とりあえずサンプルとして [simpleapp-springboot-java repository](https://github.com/yaggytter/simpleapp-springboot-java) をフォークして使ってください。シンプルな Spring Boot のサンプルです。

- 環境テンプレートを使って、 AWS Proton で環境アカウント側に環境を作ってください。以下が具体的なやり方です。

```
### まず、管理アカウント側を操作できるように AWS CLI を使えるように準備してください。
### これは各自でやってください

# その後、 以下のように、 AWS Proton の CLI を実行するための準備をします。
$ cd ec2-autoscaling
$ AWS_ACCOUNT_ID=`aws sts get-caller-identity|jq -r ".Account"`
$ AWS_REGION='REPLACE_TO_TARGET_REGION'
# いまのところ、 AWS_REGION は "ap-northeast-1" じゃやないと動きません。 AMI ID が東京リージョン専用になっているためです。

# 環境テンプレートのがわを AWS Proton 上に作成します。
$ aws proton create-environment-template \
  --region ${AWS_REGION} \
  --name "public-vpc-with-security" \
  --display-name "PublicVPCwithSecurity" \
  --description "VPC with Public Access and Security"

# 実際のテンプレートを S3 にアップロードします。
$ tar -zcvf env-template.tar.gz environment/
$ aws s3 cp env-template.tar.gz s3://proton-cli-templates-${AWS_ACCOUNT_ID}/env-template.tar.gz \
--region ${AWS_REGION}
$ rm env-template.tar.gz

# S3 のテンプレートをもとに、 AWS Proton に新しいバージョンとして登録します。
$ aws proton create-environment-template-version \
  --region ap-northeast-1 \
  --template-name "public-vpc-with-security" \
  --description "Version 1" \
  --source s3="{bucket=proton-cli-templates-${AWS_ACCOUNT_ID},key=env-template.tar.gz}"

# 登録したテンプレートのステータスを、公開ステータスにして使えるようにします。
$ aws proton update-environment-template-version \
  --region ap-northeast-1 \
  --template-name "public-vpc-with-security" \
  --major-version "1" \
  --minor-version "0" \
  --status "PUBLISHED"

```

- 環境アカウントと管理アカウントを接続します。環境アカウント側からリクエストを送って、管理アカウントで承認します。
  - https://ap-northeast-1.console.aws.amazon.com/proton/home#/settings/environment-account-connections
- AWS Proton のコンソールを利用して、いま登録した環境を環境アカウント側に作成します。前もって環境アカウントと管理アカウントは接続しておく必要があります。
  - https://ap-northeast-1.console.aws.amazon.com/proton/home#/environments

次はサービスです。

```
# サービステンプレートのがわを作成します。
$ aws proton create-service-template \
  --region ${AWS_REGION} \
  --name "ec2-autoscaling" \
  --display-name "EC2AutoScalingService" \
  --description "EC2 with an Application Load Balancer"

# 実際のテンプレートを S3 にアップロードします。
$ tar -zcvf svc-template.tar.gz service/
$ aws s3 cp svc-template.tar.gz s3://proton-cli-templates-${AWS_ACCOUNT_ID}/svc-template.tar.gz --region ${AWS_REGION}
$ rm svc-template.tar.gz

# S3 のテンプレートをもとに、 AWS Proton に新しいバージョンとして登録します。
$ aws proton create-service-template-version \
  --region ${AWS_REGION} \
  --template-name "ec2-autoscaling" \
  --source s3="{bucket=proton-cli-templates-${AWS_ACCOUNT_ID},key=svc-template.tar.gz}" \
  --compatible-environment-templates '[{"templateName":"public-vpc-with-security","majorVersion":"1"}]' \
  --description "Version 1"

# 登録したテンプレートのステータスを、公開ステータスにして使えるようにします。
$ aws proton update-service-template-version \
  --region ${AWS_REGION} \
  --template-name "ec2-autoscaling" \
  --major-version "1" \
  --minor-version "0" \
  --status "PUBLISHED"

```

- AWS Proton のコンソールを利用して、いま登録したサービスを先ほど作成した環境上に作成します。サービスは環境側に作成されますが、パイプラインは管理アカウント上に作成されます。
  - https://ap-northeast-1.console.aws.amazon.com/proton/home#/services

## AWS Proton 用のテンプレートのデバッグのしかた

AWS Proton 用のテンプレート jinja2 を使ってプレースホルダの置き換えを行っています。そのため、そのままの状態では CloudFormation テンプレートとしては機能しません。

'jinja2cfn.py' という簡易的な置換スクリプトを用意しているので、これを使ってプレースホルダを置き換えて、通常の CloudFormation テンプレートとしてデバッグしていきましょう。

- 'debug/envdata.py' を自分の環境用に書き換えます
- 以下のコマンドを実行して、 AWS Proton のプレースホルダ置き換え作業をエミュレートして、 tmp.yaml を生成します

```
$ pip install Jinja2
$ python ../debug/jinja2cfn.py ./service/instance_infrastructure/cloudformation.yaml > ./tmp.yaml
```

- tmp.yaml を通常の CloudFormation テンプレートとしてデバッグしていきましょう。

## TODO

- IAM Role の権限に強い権限を与えすぎているので、最小権限にする
