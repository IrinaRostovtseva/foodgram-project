def write_into_file(filename, ingredients):
    products = {}
    for item in ingredients:
        title = item['ingredients__title']
        amount = item['ingredient__amount']
        if title not in products:
            unit = item['ingredients__unit']
            products[title] = [amount, unit]
        else:
            products[title][0] += amount
    with open(filename, 'w') as shop_list:
        shop_list.writelines(' Продукт (ед.измерения) - количество' + '\n')
        shop_list.writelines('------------------------------------' + '\n')
        for key in products:
            line = f'{key} ({products[key][1]}) - {products[key][0]}'
            shop_list.writelines('+ ' + line + '\n')
