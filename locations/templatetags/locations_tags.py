#coding:utf-8
from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static
from locations.models import ZipCode,AdministrativeArea

register = template.Library()

class AdministrativeAreaPicNode(template.Node):
    def __init__(self,aa,width,height):
        self.aa = template.Variable(aa)
        self.width = width
        self.height = height
    def render(self,context):
        aa = self.aa.resolve(context)
        if aa is None:
            return ''
        #width = str(context[self.width])
        #height = str(context[self.height])
        width = str(self.width)
        height = str(self.height)

        # 若aa为镇级,取区县级
        while aa.administrative_level >=4:
            aa = aa.parent
        aa_id = aa.id

        base_name = 'images/aa_boundry/'
        name = str(aa_id) + '/' + width + '_' + height + '.png'

        url = static(base_name + name)
        return url

@register.tag(name="aa_boundry_pic_url")
def do_aa_boundry_pic(parser,token):
    try:
        tag_name,aa,width,height = token.split_contents()

    except ValueError:
        msg = '%r tag requires three args: aa,width,height' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
        
    return AdministrativeAreaPicNode(aa,width,height)


class ZipcodePicNode(template.Node):
    def __init__(self,zipcode,width,height,overlay_type):
        self.zipcode = template.Variable(zipcode)
        self.width = width
        self.height = height
        self.overlay_type = overlay_type
    def render(self,context):
        if self.zipcode.resolve(context) is None:
            return ''

        zp =str(self.zipcode.resolve(context))
        width = str(self.width)
        height = str(self.height)
        overlay_type = str(self.overlay_type)

        #zipcode 为6位
        if len(zp) != 6:
            return ''

        base_name = 'img/zipcode_pic/'
        # if zipcode = 123456, name like '12/34/56/160_80_1.png'
        name = "%s/%s/%s/%s_%s_%s.png" % (zp[0:2], zp[2:4], zp[4:], width, height, overlay_type)

        url = static(base_name + name)
        return url

@register.tag(name="zipcode_pic_url")
def do_zipcode_pic_url(parser,token):
    try:
        tag_name,zipcode,width,height,overlay_type = token.split_contents()
    except ValueError:
        msg = '%r tag requires four args: zipcode,width,height,overlay_type' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)

    return ZipcodePicNode(zipcode,width,height,overlay_type)

