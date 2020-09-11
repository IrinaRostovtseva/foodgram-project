def write_into_file(filename, ingredients):
    with open(filename, 'w') as shop_list:
        shop_list.write(' Продукт (ед.измерения) - количество \n')
        shop_list.write('-------------------------------------\n')
        for ingredient in ingredients:
            title = ingredient['ingredient__title']
            unit = ingredient['ingredient__unit']
            amount = ingredient['amount__sum']
            line = f'{title} ({unit}) - {amount}'
            shop_list.write('+ ' + line + '\n')
