#!/usr/bin/python3
# -*- coding: utf-8 -*-

# requires self.update_subscribers to be defined
def updater(func):
    def _updater(self, *args, **kwargs):
        func(self, *args, **kwargs)
        for subscriber in self.update_subscribers:
            try:
                update_func = getattr(subscriber, '{}_updated'.format(func.__name__))
                update_func()
            except AttributeError as e:
                print(e)
    return _updater