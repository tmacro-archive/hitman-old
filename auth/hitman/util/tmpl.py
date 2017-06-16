from flask import render_template
from functools import wraps

def templated(template=None):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			template_name = template

			ctx = f(*args, **kwargs)
			if ctx is None:
				ctx = {}
			elif not isinstance(ctx, dict):
				return ctx
			return render_template(template_name, **ctx)
		return decorated_function
	return decorator