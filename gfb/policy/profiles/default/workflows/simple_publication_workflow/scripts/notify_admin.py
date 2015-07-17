## Script (Python) "notify_admin"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
view = context.restrictedTraverse('gfbview')
view.mail_wf_change(state_change)
