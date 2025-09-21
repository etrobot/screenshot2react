import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Image from "next/image"

export function CreativeStudioTemplate() {
  return (
    <div className="bg-black text-white min-h-screen">
      {/* Header */}
      <header className="container mx-auto px-6 py-6">
        <nav className="flex justify-between items-center">
          <div className="text-2xl font-bold">STUDIO</div>
          <div className="hidden md:flex space-x-8">
            <a href="#work" className="hover:text-yellow-400 transition-colors">Work</a>
            <a href="#services" className="hover:text-yellow-400 transition-colors">Services</a>
            <a href="#team" className="hover:text-yellow-400 transition-colors">Team</a>
            <a href="#contact" className="hover:text-yellow-400 transition-colors">Contact</a>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative container mx-auto px-6 py-20">
        <div className="absolute inset-0 -mx-6 rounded-2xl overflow-hidden">
          <Image
            src="/creative-studio-hero.png"
            alt="Creative Studio Hero Background"
            fill
            className="object-cover opacity-20"
            priority
          />
        </div>
        <div className="relative z-10 grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <Badge className="mb-6 bg-yellow-400/20 text-yellow-400 border-yellow-400/30">
              Creative Agency
            </Badge>
            <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
              WE CREATE
              <br />
              <span className="text-yellow-400">AMAZING</span>
              <br />
              THINGS
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-lg">
              A creative studio that brings bold ideas to life. We specialize in branding, 
              digital experiences, and visual storytelling that makes an impact.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="bg-yellow-400 text-black hover:bg-yellow-500 font-semibold">
                See Our Work
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-black">
                Start a Project
              </Button>
            </div>
          </div>
          
          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-yellow-400 to-orange-500 h-32 rounded-lg"></div>
                <div className="bg-gradient-to-br from-purple-500 to-pink-500 h-48 rounded-lg"></div>
              </div>
              <div className="space-y-4 mt-8">
                <div className="bg-gradient-to-br from-blue-500 to-cyan-500 h-48 rounded-lg"></div>
                <div className="bg-gradient-to-br from-green-500 to-emerald-500 h-32 rounded-lg"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services */}
      <section className="container mx-auto px-6 py-20 border-t border-gray-800">
        <h2 className="text-4xl font-bold mb-12">What We Do</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[
            { title: "Branding", desc: "Complete brand identity and strategy" },
            { title: "Web Design", desc: "Modern, responsive website design" },
            { title: "Digital Art", desc: "Custom illustrations and graphics" },
            { title: "Motion", desc: "Animation and video production" },
          ].map((service, index) => (
            <div key={index} className="group cursor-pointer">
              <div className="border border-gray-800 p-6 rounded-lg group-hover:border-yellow-400 transition-all">
                <div className="w-12 h-12 bg-yellow-400 rounded-lg mb-4 flex items-center justify-center">
                  <span className="text-black font-bold">{index + 1}</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">{service.title}</h3>
                <p className="text-gray-400">{service.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Portfolio Grid */}
      <section className="container mx-auto px-6 py-20">
        <h2 className="text-4xl font-bold mb-12">Recent Work</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <div key={item} className="group cursor-pointer">
              <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg overflow-hidden group-hover:scale-105 transition-transform">
                <div className="h-64 bg-gradient-to-br from-yellow-400/20 to-orange-500/20 flex items-center justify-center">
                  <span className="text-6xl opacity-50">🎨</span>
                </div>
                <div className="p-6">
                  <h3 className="font-semibold mb-2">Project {item}</h3>
                  <p className="text-gray-400 text-sm">Creative Direction</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-12 border-t border-gray-800">
        <div className="text-center">
          <h3 className="text-2xl font-bold mb-4">Ready to Create Something Amazing?</h3>
          <Button className="bg-yellow-400 text-black hover:bg-yellow-500 font-semibold">
            Let's Talk
          </Button>
        </div>
      </footer>
    </div>
  )
}
