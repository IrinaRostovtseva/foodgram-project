def write_into_file(filename, ingredients):
    with open(filename, 'w') as shop_list:
        shop_list.writelines('Продукт (ед.измерения) - количество' + '\n')
        shop_list.writelines('------------------------------------' + '\n')
        for ingredient in ingredients:
            title = ingredient['ingredients__title']
            amount = ingredient['ingredient__amount__sum']
            unit = ingredient['ingredients__unit']
            line = f'{title} ({unit}) - {amount}'
            shop_list.writelines('+ ' + line + '\n')
