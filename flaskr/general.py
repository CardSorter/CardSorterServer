def fetchallClean(curr):
    """
    for every entry for every row checks if entry is string and strips it
    :param curr: (self.cur)
    :return: the fetched thing with stripped strings
    """
    data = curr.fetchall()
    if data:
        return  [[i.strip() if isinstance(i, str) else i for i in j] for j in data]
    else:
        return []

def fetchoneClean(curr):
    """like the one above, but for one"""
    data = curr.fetchone()
    if data:
        return [i.strip() if isinstance(i, str) else i for i in data]
    else:
        return []
