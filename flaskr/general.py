def fetchallClean(curr):
    """
    for every entry for every row checks if entry is string and strips it
    :param curr: (self.cur)
    :return: the fetched thing with stripped strings
    """
    return  [[i.strip() if isinstance(i, str) else i for i in j] for j in curr.fetchall()]

def fetchoneClean(curr):
    """like the one above, but for one"""
    return [i.strip() if isinstance(i, str) else i for i in curr.fetchone()]
