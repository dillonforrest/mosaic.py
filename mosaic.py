"""

Inspiration:  ~/Photo-Mosaic/sourcecode.py

"""

#!/usr/bin/python
import Image, sys, os, math

class Mosaic():

	def __init__(self):
		self.tile_colors = []
		self.tile_pic_avgs = {}
		self.avg_color_list = []

	def setUp(self, params):
		"""
		params[1] = path of target photo 
		params[2] = path of tile photos
		params[3] = number tiles across for final mosaic
		params[4] = number tiles down for final mosaic
		"""
		self.tg_path = os.path.abspath(params[1])
		self.tiles_dir_path = os.path.abspath(params[2])
		self.tg_img = Image.open(self.tg_path)
		self.tg_rez = self.tg_img.size
		self.tg_data = self.tg_img.load()
		self.n_tiles_acr = int(params[3])
		self.n_tiles_down = int(params[4])
		self.tile_width = self.tg_rez[0] / self.n_tiles_acr
		self.tile_height = self.tg_rez[1] / self.n_tiles_down
		self.pic_width = self.tile_width * self.n_tiles_acr # remove ancillary pix
		self.pic_height = self.tile_height * self.n_tiles_down # remove ancillary pix
	
	def findAvgColor(self, img, bounds):
		color_sums = [0,0,0] # red, green, blue
		img = img.load()
		num_px = (bounds[2]-bounds[0]) * (bounds[3]-bounds[1])
		for x in range(bounds[0], bounds[2]):
			for y in range(bounds[1], bounds[3]):
				color_sums[0] += img[x,y][0]
				color_sums[1] += img[x,y][1]
				color_sums[2] += img[x,y][2]
		avg_color = (color_sums[0]/num_px, color_sums[1]/num_px, color_sums[2]/num_px)
		return avg_color
	
	def createColorMatrix(self):
		for x in range(self.n_tiles_acr):
			self.tile_colors.append([])
			for y in range(self.n_tiles_down):
				bounds = (
					x * self.tile_width, y * self.tile_height,
					(x+1) * self.tile_width, (y+1) * self.tile_height
				)
				self.tile_colors[x].append(self.findAvgColor(self.tg_img, bounds))
	
	def makeProof(self):
		proof = Image.new(self.tg_img.mode, (self.pic_width,self.pic_height))
		for x in range(self.n_tiles_acr):
			for y in range(self.n_tiles_down):
				block = (
					x * self.tile_width, y * self.tile_height,
					(x+1) * self.tile_width, (y+1) * self.tile_height
				)
				color = self.tile_colors[x][y]
				proof.paste(color, block)
		proof.save(os.path.dirname(self.tg_path) + 'proof.png')
			
	def colorDistance(self, color1, color2):
		distance = math.sqrt(
			(color1[0]-color2[0])**2 +
			(color1[1]-color2[1])**2 +
			(color1[2]-color2[2])**2
		)
		return distance
		
	def isImageFile(self, file_name):
		file_name = file_name.lower()
		if file_name.endswith('jpg'):
			return True
		else: return False
		
	def avgTiles(self):
		for file in os.listdir(self.tiles_dir_path):
			if self.isImageFile(file):
				file_path = os.path.join(self.tiles_dir_path, file)
				img = Image.open(file_path)
				self.tile_pic_avgs[file] = self.findAvgColor(img,
					(0,0,img.size[0],img.size[1]))
			
	def findClosestTile(self, tile_on_target):
		min_color_dist = 442 # Maximum distance between (255,255,255) and (0,0,0)
		min_dist_tile = self.tile_pic_avgs.keys()[0]
		for tile in self.tile_pic_avgs:
			dist = self.colorDistance(self.tile_pic_avgs[tile], tile_on_target)
			if dist < min_color_dist:
				min_color_dist = dist
				min_dist_tile = tile
		return min_dist_tile
		
	def createFinal(self):
		self.final_pic = Image.new(self.tg_img.mode, (self.pic_width,self.pic_height))
		for x in range(self.n_tiles_acr):
			for y in range(self.n_tiles_down):
				tile = self.findClosestTile(self.tile_colors[x][y])
				tile_img = Image.open(os.path.join(self.tiles_dir_path, tile))
				tile_img = tile_img.resize((self.tile_width,self.tile_height),
					Image.ANTIALIAS)
				block = (x*self.tile_width, y*self.tile_height,
					(x+1)*self.tile_width, (y+1)*self.tile_height)
				self.final_pic.paste(tile_img, block)
		self.final_pic.save('final.png')
	
	def generate(self, params):
		self.setUp(params)
		self.createColorMatrix()
		self.makeProof()
		self.avgTiles()
		self.createFinal()

if __name__ == "__main__":
	mosaic = Mosaic()
	if len(sys.argv) == 5:
		mosaic.generate(sys.argv)

print "done"